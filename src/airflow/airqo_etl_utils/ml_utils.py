import json
from datetime import datetime

import gcsfs
import joblib
import mlflow
import numpy as np
import optuna
import pandas as pd
import pymongo as pm
from lightgbm import LGBMRegressor
from scipy.stats import skew
from sklearn.metrics import mean_squared_error

from .config import configuration

fixed_columns = ["site_id"]
project_id = configuration.GOOGLE_CLOUD_PROJECT_ID
bucket = configuration.FORECAST_MODELS_BUCKET
environment = configuration.ENVIRONMENT


def get_trained_model_from_gcs(project_name, bucket_name, source_blob_name):
    fs = gcsfs.GCSFileSystem(project=project_name)
    fs.ls(bucket_name)
    with fs.open(bucket_name + "/" + source_blob_name, "rb") as handle:
        job = joblib.load(handle)
    return job


def upload_trained_model_to_gcs(
    trained_model, project_name, bucket_name, source_blob_name
):
    fs = gcsfs.GCSFileSystem(project=project_name)
    try:
        fs.rename(
            f"{bucket_name}/{source_blob_name}",
            f"{bucket_name}/{datetime.now()}-{source_blob_name}",
        )
        print("Bucket: previous model is backed up")
    except:
        print("Bucket: No file to updated")

    # store new model
    with fs.open(bucket_name + "/" + source_blob_name, "wb") as handle:
        job = joblib.dump(trained_model, handle)


def upload_mapping_to_gcs(mapping_dict, project_name, bucket_name, source_blob_name):
    fs = gcsfs.GCSFileSystem(project=project_name)
    mapping_dict = json.dumps(mapping_dict)
    with fs.open(bucket_name + "/" + source_blob_name, "w") as f:
        f.write(mapping_dict)


def get_mapping_from_gcs(project_name, bucket_name, source_blob_name):
    fs = gcsfs.GCSFileSystem(project=project_name)
    with fs.open(bucket_name + "/" + source_blob_name, "r") as f:
        mapping_dict = json.load(f)
    return mapping_dict


class ForecastUtils:
    # FORECAST MODEL TRAINING UTILS
    @staticmethod
    def preprocess_training_data(data, frequency):
        data["timestamp"] = pd.to_datetime(data["timestamp"])
        data["pm2_5"] = data.groupby("device_id")["pm2_5"].transform(
            lambda x: x.interpolate(method="linear", limit_direction="both")
        )
        if frequency == "daily":
            data = (
                data.groupby(["device_id"])
                .resample("D", on="timestamp")
                .mean(numeric_only=True)
            )
            data.reset_index(inplace=True)
            data["pm2_5"] = data.groupby("device_id")["pm2_5"].transform(
                lambda x: x.interpolate(method="linear", limit_direction="both")
            )
        data = data.dropna(subset=["pm2_5"])
        return data

    @staticmethod
    def feature_eng_training_data(data, target_column, frequency):
        def get_lag_features(df, target_col, freq):
            df = df.sort_values(by=["device_id", "timestamp"])

            if freq == "daily":
                shifts = [1, 2, 3, 7, 14]
                for s in shifts:
                    df[f"pm2_5_last_{s}_day"] = df.groupby(["device_id"])[
                        target_col
                    ].shift(s)

                shifts = [2, 3, 7, 14]
                functions = ["mean", "std", "max", "min"]
                for s in shifts:
                    for f in functions:
                        df[f"pm2_5_{f}_{s}_day"] = (
                            df.groupby(["device_id"])[target_col]
                            .shift(1)
                            .rolling(s)
                            .agg(f)
                        )
            elif freq == "hourly":
                shifts = [1, 2, 6, 12]
                for s in shifts:
                    df[f"pm2_5_last_{s}_hour"] = df.groupby(["device_id"])[
                        target_col
                    ].shift(s)

                shifts = [3, 6, 12, 24]
                functions = ["mean", "std", "median", "skew"]
                for s in shifts:
                    for f in functions:
                        df[f"pm2_5_{f}_{s}_hour"] = (
                            df.groupby(["device_id"])[target_col]
                            .shift(1)
                            .rolling(s)
                            .agg(f)
                        )
            else:
                raise ValueError("Invalid frequency")

            return df

        def count_encode_categorical_features(df):
            device_id_mappings, site_id_mappings, device_category_mappings = {}, {}, {}
            for col in ["device_id", "site_id", "device_category"]:
                counts = df[col].value_counts()
                count_dict = dict(zip(counts.index, counts.values))
                if col == "device_id":
                    device_id_mappings = count_dict
                elif col == "site_id":
                    site_id_mappings = count_dict
                elif col == "device_category":
                    device_category_mappings = count_dict
                df[f"{col}"] = df[col].map(count_dict)
            mappings = [device_id_mappings, site_id_mappings, device_category_mappings]
            for mapping in mappings:
                upload_mapping_to_gcs(mapping, project_id, bucket, f"{mapping}.json")

            return df

        def get_time_and_cyclic_features(df, freq):
            attributes = ["year", "month", "day", "dayofweek", "hour"]
            max_vals = [2023, 12, 31, 6, 23]
            if freq == "hourly":
                attributes.append("minute")
                max_vals.append(59)
            for a, m in zip(attributes, max_vals):
                df[a] = df["timestamp"].dt.__getattribute__(a)
                df[a + "_sin"] = np.sin(2 * np.pi * df[a] / m)
                df[a + "_cos"] = np.cos(2 * np.pi * df[a] / m)

            df["week"] = df["timestamp"].dt.isocalendar().week
            df["week_sin"] = np.sin(2 * np.pi * df["week"] / 52)
            df["week_cos"] = np.cos(2 * np.pi * df["week"] / 52)
            df.drop(columns=attributes, inplace=True)
            return df

        data["timestamp"] = pd.to_datetime(data["timestamp"])
        df_tmp = get_lag_features(data, target_column, frequency)
        df_tmp = count_encode_categorical_features(df_tmp)
        df_tmp = get_time_and_cyclic_features(df_tmp, frequency)

        return df_tmp

    @staticmethod
    def train_and_save_forecast_models(train, frequency):
        """
        Perform the actual training for hourly data
        """
        train["timestamp"] = pd.to_datetime(train["timestamp"])
        train = train.sort_values(by=["device_id", "timestamp"])
        features = [c for c in train.columns if c not in ["timestamp", "pm2_5"]]
        print(features)
        target_col = "pm2_5"
        train_data, validation_data, test_data = (
            pd.DataFrame(),
            pd.DataFrame(),
            pd.DataFrame(),
        )
        for device in train["device_id"].unique():
            device_df = train[train["device_id"] == device]
            device_df = device_df.sort_values(by="timestamp")
            months = device_df["timestamp"].dt.month.unique()
            train_months = val_months = test_months = 0
            if frequency == "hourly":
                train_months = months[:8]
                val_months = months[8:9]
                test_months = months[9:]
            elif frequency == "daily":
                train_months = months[:10]
                val_months = months[10:11]
                test_months = months[11:]

            train_df = device_df[device_df["timestamp"].dt.month.isin(train_months)]
            val_df = device_df[device_df["timestamp"].dt.month.isin(val_months)]
            test_df = device_df[device_df["timestamp"].dt.month.isin(test_months)]
            train_data = pd.concat([train_data, train_df])
            validation_data = pd.concat([validation_data, val_df])
            test_data = pd.concat([test_data, test_df])

        train_data.drop(columns=["timestamp"], axis=1, inplace=True)
        validation_data.drop(columns=["timestamp"], axis=1, inplace=True)
        test_data.drop(columns=["timestamp"], axis=1, inplace=True)

        train_target, validation_target, test_target = (
            train_data[target_col],
            validation_data[target_col],
            test_data[target_col],
        )

        mlflow.set_tracking_uri(configuration.MLFLOW_TRACKING_URI)
        mlflow.set_experiment(f"LGBM_{frequency}_forecast_model_{environment}")
        registered_model_name = f"LGBM_{frequency}_forecast_model_{environment}"

        mlflow.lightgbm.autolog(registered_model_name=registered_model_name)

        sampler = optuna.samplers.TPESampler()
        pruner = optuna.pruners.SuccessiveHalvingPruner(
            min_resource=10, reduction_factor=2, min_early_stopping_rate=0
        )
        study = optuna.create_study(
            direction="minimize", study_name="LGBM", sampler=sampler, pruner=pruner
        )

        def objective(trial):
            param_grid = {
                "colsample_bytree": trial.suggest_uniform("colsample_bytree", 0.1, 1),
                "reg_alpha": trial.suggest_uniform("reg_alpha", 0, 10),
                "reg_lambda": trial.suggest_uniform("reg_lambda", 0, 10),
                "n_estimators": trial.suggest_categorical("n_estimators", [10000]),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3),
                "num_leaves": trial.suggest_int("num_leaves", 20, 3000, step=20),
                "max_depth": trial.suggest_int("max_depth", 3, 12),
                "min_split_gain": trial.suggest_float("min_gain_to_split", 0, 15),
            }

            score = 0
            for step in range(4):
                lgb_reg = LGBMRegressor(
                    objective="regression",
                    n_jobs=2,
                    random_state=42,
                    **param_grid,
                    verbosity=2,
                )
                lgb_reg.fit(
                    train_data[features],
                    train_target,
                    categorical_feature=["device_id", "site_id", "device_category"],
                    eval_set=[(test_data[features], test_target)],
                    eval_metric="rmse",
                )

                val_preds = lgb_reg.predict(validation_data[features])
                score = mean_squared_error(validation_target, val_preds)
                if trial.should_prune():
                    raise optuna.TrialPruned()

            return score

        study.optimize(objective, n_trials=150)

        with mlflow.start_run():
            best_params = study.best_params
            print(f"Best params are {best_params}")
            clf = LGBMRegressor(
                n_estimators=best_params["n_estimators"],
                learning_rate=best_params["learning_rate"],
                colsample_bytree=best_params["colsample_bytree"],
                reg_alpha=best_params["reg_alpha"],
                reg_lambda=best_params["reg_lambda"],
                max_depth=best_params["max_depth"],
                random_state=42,
                verbosity=2,
            )

            clf.fit(
                train_data[features],
                train_target,
                eval_set=[(test_data[features], test_target)],
                eval_metric="rmse",
                categorical_feature=["device_id", "site_id", "device_category"],
            )

            # train quantile regression models for 0.025 and 0.975 quantiles
            clf_025 = LGBMRegressor(
                n_estimators=best_params["n_estimators"],
                learning_rate=best_params["learning_rate"],
                colsample_bytree=best_params["colsample_bytree"],
                reg_alpha=best_params["reg_alpha"],
                reg_lambda=best_params["reg_lambda"],
                max_depth=best_params["max_depth"],
                random_state=42,
                verbosity=2,
                objective="quantile",
                alpha=0.025,
                metric="quantile",
            )

            clf_025.fit(
                train_data[features],
                train_target,
                eval_set=[(test_data[features], test_target)],
                categorical_feature=["device_id", "site_id", "device_category"],
            )

            clf_975 = LGBMRegressor(
                n_estimators=best_params["n_estimators"],
                learning_rate=best_params["learning_rate"],
                colsample_bytree=best_params["colsample_bytree"],
                reg_alpha=best_params["reg_alpha"],
                reg_lambda=best_params["reg_lambda"],
                max_depth=best_params["max_depth"],
                random_state=42,
                verbosity=2,
                objective="quantile",
                alpha=0.975,
                metric="quantile",
            )

            clf_975.fit(
                train_data[features],
                train_target,
                eval_set=[(test_data[features], test_target)],
                categorical_feature=["device_id", "site_id", "device_category"],
            )

            upload_trained_model_to_gcs(
                clf, project_id, bucket, "hourly_forecast_model.pkl"
            )

    #### FORECAST JOB UTILS ####

    @staticmethod
    def preprocess_historical_data(data, frequency):
        data["timestamp"] = pd.to_datetime(data["timestamp"])
        data["device_number"] = data["device_number"].astype(str)
        data["pm2_5"] = data.groupby(fixed_columns + ["device_number"])[
            "pm2_5"
        ].transform(lambda x: x.interpolate(method="linear", limit_direction="both"))
        if frequency == "hourly":
            data.sort_values(
                by=fixed_columns + ["device_number", "timestamp"], inplace=True
            )
        elif frequency == "daily":
            data = (
                data.groupby(fixed_columns + ["device_number"])
                .resample("D", on="timestamp")
                .mean(numeric_only=True)
            )
            data.reset_index(inplace=True)
            data["pm2_5"] = data.groupby(fixed_columns + ["device_number"])[
                "pm2_5"
            ].transform(
                lambda x: x.interpolate(method="linear", limit_direction="both")
            )
            data.sort_values(
                by=fixed_columns + ["device_number", "timestamp"], inplace=True
            )
        else:
            raise ValueError("Invalid frequency argument")
        data["device_number"] = data["device_number"].astype(int)
        data = data.dropna(subset=["pm2_5"])
        return data

    @staticmethod
    def get_lag_features(df_tmp, TARGET_COL, frequency):
        df_tmp["timestamp"] = pd.to_datetime(df_tmp["timestamp"])
        df_tmp = df_tmp.sort_values(by=fixed_columns + ["device_number", "timestamp"])
        if frequency == "hourly":
            shifts = [1, 2]
            for s in shifts:
                df_tmp[f"pm2_5_last_{s}_hour"] = df_tmp.groupby(["device_number"])[
                    TARGET_COL
                ].shift(s)

            shifts = [6, 12, 24, 48]
            functions = ["mean", "std", "median", "skew"]
            for s in shifts:
                for f in functions:
                    df_tmp[f"pm2_5_{f}_{s}_hour"] = (
                        df_tmp.groupby(["device_number"])[TARGET_COL]
                        .shift(1)
                        .rolling(s)
                        .agg(f)
                    )
        elif frequency == "daily":
            shifts = [1, 2]
            for s in shifts:
                df_tmp[f"pm2_5_last_{s}_day"] = df_tmp.groupby(["device_number"])[
                    TARGET_COL
                ].shift(s)
            shifts = [3, 7, 14, 30]
            functions = ["mean", "std", "max", "min"]
            for s in shifts:
                for f in functions:
                    df_tmp[f"pm2_5_{f}_{s}_day"] = (
                        df_tmp.groupby(["device_number"])[TARGET_COL]
                        .shift(1)
                        .rolling(s)
                        .agg(f)
                    )
        else:
            raise ValueError("Invalid frequency argument")
        print("Adding lag features")
        return df_tmp

    @staticmethod
    def get_time_features(df_tmp, frequency):
        df_tmp["timestamp"] = pd.to_datetime(df_tmp["timestamp"])
        attributes = ["year", "month", "day", "dayofweek"]
        if frequency == "hourly":
            attributes.extend(["hour", "minute"])
        for a in attributes:
            df_tmp[a] = df_tmp["timestamp"].dt.__getattribute__(a)

        df_tmp["week"] = df_tmp["timestamp"].dt.isocalendar().week
        print("Adding other features")
        return df_tmp

    @staticmethod
    def generate_hourly_forecasts(data, project_name, bucket_name, source_blob_name):
        data["timestamp"] = pd.to_datetime(data["timestamp"])

        def get_new_row(df, device1, model):
            last_row = df[df["device_number"] == device1].iloc[-1]
            new_row = pd.Series(index=last_row.index, dtype="float64")
            for i in fixed_columns:
                new_row[i] = last_row[i]
            new_row["timestamp"] = last_row["timestamp"] + pd.Timedelta(hours=1)
            new_row["device_number"] = device1
            new_row[f"pm2_5_last_1_hour"] = last_row["pm2_5"]
            new_row[f"pm2_5_last_2_hour"] = last_row[f"pm2_5_last_{1}_hour"]

            shifts = [6, 12, 24, 48]
            functions = ["mean", "std", "median", "skew"]
            for s in shifts:
                for f in functions:
                    if f == "mean":
                        new_row[f"pm2_5_{f}_{s}_hour"] = (
                            last_row["pm2_5"]
                            + last_row[f"pm2_5_{f}_{s}_hour"] * (s - 1)
                        ) / s
                    elif f == "std":
                        new_row[f"pm2_5_{f}_{s}_hour"] = (
                            np.sqrt(
                                (last_row["pm2_5"] - last_row[f"pm2_5_mean_{s}_hour"])
                                ** 2
                                + (last_row[f"pm2_5_{f}_{s}_hour"] ** 2 * (s - 1))
                            )
                            / s
                        )
                    elif f == "median":
                        new_row[f"pm2_5_{f}_{s}_hour"] = np.median(
                            np.append(
                                last_row["pm2_5"], last_row[f"pm2_5_{f}_{s}_hour"]
                            )
                        )
                    elif f == "skew":
                        new_row[f"pm2_5_{f}_{s}_hour"] = skew(
                            np.append(
                                last_row["pm2_5"], last_row[f"pm2_5_{f}_{s}_hour"]
                            )
                        )

            attributes = ["year", "month", "day", "dayofweek", "hour", "minute"]
            for a in attributes:
                new_row[a] = new_row["timestamp"].__getattribute__(a)
                new_row["week"] = new_row["timestamp"].isocalendar().week

            new_row["pm2_5"] = model.predict(
                new_row.drop(fixed_columns + ["timestamp", "pm2_5"]).values.reshape(
                    1, -1
                )
            )[0]
            return new_row

        forecasts = pd.DataFrame()
        forecast_model = get_trained_model_from_gcs(
            project_name, bucket_name, source_blob_name
        )
        df_tmp = data.copy()
        for device in df_tmp["device_number"].unique():
            test_copy = df_tmp[df_tmp["device_number"] == device]
            for i in range(int(configuration.HOURLY_FORECAST_HORIZON)):
                new_row = get_new_row(test_copy, device, forecast_model)
                test_copy = pd.concat(
                    [test_copy, new_row.to_frame().T], ignore_index=True
                )
            forecasts = pd.concat([forecasts, test_copy], ignore_index=True)

        forecasts["device_number"] = forecasts["device_number"].astype(int)
        forecasts["pm2_5"] = forecasts["pm2_5"].astype(float)
        forecasts.rename(columns={"timestamp": "time"}, inplace=True)
        forecasts["time"] = pd.to_datetime(forecasts["time"], utc=True)
        current_time = datetime.utcnow()
        current_time_utc = pd.Timestamp(current_time, tz="UTC")
        result = forecasts[fixed_columns + ["time", "pm2_5", "device_number"]][
            forecasts["time"] >= current_time_utc
        ]

        return result

    @staticmethod
    def generate_daily_forecasts(data, project_name, bucket_name, source_blob_name):
        data["timestamp"] = pd.to_datetime(data["timestamp"])

        def get_new_row(df_tmp, device, model):
            last_row = df_tmp[df_tmp["device_number"] == device].iloc[-1]
            new_row = pd.Series(index=last_row.index, dtype="float64")
            for i in fixed_columns:
                new_row[i] = last_row[i]
            new_row["timestamp"] = last_row["timestamp"] + pd.Timedelta(days=1)
            new_row["device_number"] = device
            new_row[f"pm2_5_last_1_day"] = last_row["pm2_5"]
            new_row[f"pm2_5_last_2_day"] = last_row[f"pm2_5_last_{1}_day"]

            shifts = [3, 7, 14, 30]
            functions = ["mean", "std", "max", "min"]
            for s in shifts:
                for f in functions:
                    if f == "mean":
                        new_row[f"pm2_5_{f}_{s}_day"] = (
                            last_row["pm2_5"] + last_row[f"pm2_5_{f}_{s}_day"] * (s - 1)
                        ) / s
                    elif f == "std":
                        new_row[f"pm2_5_{f}_{s}_day"] = (
                            np.sqrt(
                                (last_row["pm2_5"] - last_row[f"pm2_5_mean_{s}_day"])
                                ** 2
                                + (last_row[f"pm2_5_{f}_{s}_day"] ** 2 * (s - 1))
                            )
                            / s
                        )
                    elif f == "max":
                        new_row[f"pm2_5_{f}_{s}_day"] = max(
                            last_row["pm2_5"], last_row[f"pm2_5_{f}_{s}_day"]
                        )
                    elif f == "min":
                        new_row[f"pm2_5_{f}_{s}_day"] = min(
                            last_row["pm2_5"], last_row[f"pm2_5_{f}_{s}_day"]
                        )

                        # Use the date of the new row to create other features
            attributes = ["year", "month", "day", "dayofweek"]
            for a in attributes:
                new_row[a] = new_row["timestamp"].__getattribute__(a)
            new_row["week"] = new_row["timestamp"].isocalendar().week

            new_row["pm2_5"] = model.predict(
                new_row.drop(fixed_columns + ["timestamp", "pm2_5"]).values.reshape(
                    1, -1
                )
            )[0]
            return new_row

        forecasts = pd.DataFrame()

        forecast_model = get_trained_model_from_gcs(
            project_name, bucket_name, source_blob_name
        )

        df_tmp = data.copy()
        for device in df_tmp["device_number"].unique():
            test_copy = df_tmp[df_tmp["device_number"] == device]
            for i in range(int(configuration.DAILY_FORECAST_HORIZON)):
                new_row = get_new_row(
                    test_copy,
                    device,
                    forecast_model,
                )
                test_copy = pd.concat(
                    [test_copy, new_row.to_frame().T], ignore_index=True
                )
            forecasts = pd.concat([forecasts, test_copy], ignore_index=True)
        forecasts["device_number"] = forecasts["device_number"].astype(int)
        forecasts["pm2_5"] = forecasts["pm2_5"].astype(float)
        forecasts.rename(columns={"timestamp": "time"}, inplace=True)
        current_time = datetime.utcnow()
        current_time_utc = pd.Timestamp(current_time, tz="UTC")
        result = forecasts[fixed_columns + ["time", "pm2_5", "device_number"]][
            forecasts["time"] >= current_time_utc
        ]

        return result

    @staticmethod
    def save_forecasts_to_mongo(data, frequency):
        timestamp = pd.to_datetime(datetime.now()).isoformat()
        device_numbers = data["device_number"].unique()
        forecast_results = [
            {
                field: data[data["device_number"] == i][field].tolist()[0]
                if field != "pm2_5" and field != "time" and field != "health_tips"
                else data[data["device_number"] == i][field].tolist()
                for field in data.columns
            }
            | {"timestamp": timestamp}
            for i in device_numbers
        ]
        client = pm.MongoClient(configuration.MONGO_URI)
        db = client[configuration.MONGO_DATABASE_NAME]
        if frequency == "hourly":
            db.hourly_forecasts.insert_many(forecast_results)
        elif frequency == "daily":
            db.daily_forecasts.insert_many(forecast_results)
        else:
            raise ValueError("Invalid frequency argument")
