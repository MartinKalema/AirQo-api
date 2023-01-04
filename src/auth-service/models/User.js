const mongoose = require("mongoose").set("debug", true);
const Schema = mongoose.Schema;
const validator = require("validator");
const bcrypt = require("bcrypt");
const jwt = require("jsonwebtoken");
const constants = require("../config/constants");
const { logObject, logElement, logText } = require("../utils/log");
const ObjectId = mongoose.Schema.Types.ObjectId;
const validations = require("../utils/validations");
const isEmpty = require("is-empty");
const { log } = require("debug");
const saltRounds = constants.SALT_ROUNDS;
const HTTPStatus = require("http-status");
const accessCodeGenerator = require("generate-password");
const { getModelByTenant } = require("../utils/multitenancy");

function oneMonthFromNow() {
  var d = new Date();
  var targetMonth = d.getMonth() + 1;
  d.setMonth(targetMonth);
  if (d.getMonth() !== targetMonth % 12) {
    d.setDate(0); // last day of previous month
  }
  return d;
}

const UserSchema = new Schema(
  {
    due_date: { type: Date },
    status: { type: String },
    address: { type: String },
    country: { type: String },
    city: { type: String },
    email: {
      type: String,
      unique: true,
      required: [true, "Email is required"],
      trim: true,
      validate: {
        validator(email) {
          return validator.isEmail(email);
        },
        message: "{VALUE} is not a valid email!",
      },
    },
    emailConfirmed: {
      type: Boolean,
      default: false,
    },
    firstName: {
      type: String,
      required: [true, "FirstName is required!"],
      trim: true,
    },
    lastName: {
      type: String,
      required: [true, "LastName is required"],
      trim: true,
    },
    userName: {
      type: String,
      required: [true, "UserName is required!"],
      trim: true,
      unique: true,
    },
    password: {
      type: String,
      required: [true, "Password is required!"],
      trim: true,
      minlength: [6, "Password is required"],
      validate: {
        validator(password) {
          return validations.passwordReg.test(password);
        },
        message: "{VALUE} is not a valid password, please check documentation!",
      },
    },
    privilege: { type: String, required: [true, "the role is required!"] },
    isActive: { type: Boolean },
    duration: { type: Date, default: oneMonthFromNow },
    networks: [
      {
        type: ObjectId,
        ref: "network",
        required: [true, "the network is required!"],
      },
    ],
    groups: [
      {
        type: ObjectId,
        ref: "group",
      },
    ],
    roles: [
      {
        type: ObjectId,
        ref: "role",
      },
    ],
    permissions: [
      {
        type: ObjectId,
        ref: "permission",
      },
    ],
    organization: {
      type: String,
      required: [true, "the organization is required!"],
    },
    long_organization: {
      type: String,
      required: [true, "the long_organization is required!"],
    },
    country: { type: String },
    phoneNumber: { type: Number },
    locationCount: { type: Number, default: 5 },
    resetPasswordToken: { type: String },
    resetPasswordExpires: { type: Date },
    jobTitle: {
      type: String,
    },
    website: { type: String },
    description: { type: String },
    category: {
      type: String,
    },
    notifications: {
      email: { type: Boolean, default: false },
      push: { type: Boolean, default: false },
      text: { type: Boolean, default: false },
      phone: { type: Boolean, default: false },
    },
    profilePicture: {
      type: String,
    },
  },
  { timestamps: true }
);

UserSchema.pre("save", function (next) {
  if (this.isModified("password")) {
    this.password = bcrypt.hashSync(this.password, saltRounds);
  }
  return next();
});

UserSchema.pre("findOneAndUpdate", function () {
  let that = this;
  const update = that.getUpdate();
  if (update.__v != null) {
    delete update.__v;
  }
  const keys = ["$set", "$setOnInsert"];
  for (const key of keys) {
    if (update[key] != null && update[key].__v != null) {
      delete update[key].__v;
      if (Object.keys(update[key]).length === 0) {
        delete update[key];
      }
    }
  }
  update.$inc = update.$inc || {};
  update.$inc.__v = 1;
});

UserSchema.pre("update", function (next) {
  if (this.isModified("password")) {
    this.password = bcrypt.hashSync(this.password, saltRounds);
  }
  return next();
});

UserSchema.index({ email: 1 }, { unique: true });
UserSchema.index({ userName: 1 }, { unique: true });

UserSchema.statics = {
  async register(args) {
    try {
      data = await this.create({
        ...args,
      });
      if (data) {
        return {
          success: true,
          data,
          message: "user created",
        };
      }
      return {
        success: true,
        data,
        message: "operation successful but user NOT successfully created",
      };
    } catch (err) {
      logObject("the error", err);
      let response = {};
      let message = "validation errors for some of the provided fields";
      let status = HTTPStatus.CONFLICT;
      if (err.keyValue) {
        Object.entries(err.keyValue).forEach(([key, value]) => {
          return (response[key] = `the ${key} must be unique`);
        });
      }

      return {
        error: response,
        message,
        success: false,
        status,
      };
    }
  },
  async list({ skip = 0, limit = 5, filter = {} } = {}) {
    try {
      const projectAll = {
        _id: 1,
        firstName: 1,
        lastName: 1,
        userName: 1,
        email: 1,
        privilege: 1,
        profilePicture: 1,
        phoneNumber: 1,
        networks: "$networks",
        access_tokens: "$access_tokens",
        permissions: "$permissions",
        roles: "$roles",
      };

      const projectSummary = {};

      const response = await this.aggregate()
        .match(filter)
        .lookup({
          from: "networks",
          localField: "_id",
          foreignField: "net_users",
          as: "networks",
        })
        .lookup({
          from: "access_tokens",
          localField: "_id",
          foreignField: "user_id",
          as: "access_tokens",
        })
        .lookup({
          from: "groups",
          localField: "_id",
          foreignField: "grp_users",
          as: "groups",
        })
        .lookup({
          from: "permissions",
          localField: "permissions",
          foreignField: "_id",
          as: "permissions",
        })
        .lookup({
          from: "roles",
          localField: "roles",
          foreignField: "_id",
          as: "roles",
        })
        .sort({ createdAt: -1 })
        .project(projectAll)
        .project({
          "networks.__v": 0,
          "networks.net_status": 0,
          "networks.net_acronym": 0,
          "networks.createdAt": 0,
          "networks.updatedAt": 0,
          "networks.net_users": 0,
          "networks.net_roles": 0,
          "networks.net_groups": 0,
          "networks.net_description": 0,
          "networks.net_departments": 0,
          "networks.net_permissions": 0,
          "networks.net_email": 0,
          "networks.net_category": 0,
          "networks.net_phoneNumber": 0,
          "networks.net_manager": 0,
        })
        .project({
          "access_tokens.__v": 0,
          "access_tokens._id": 0,
          "access_tokens.user_id": 0,
          "access_tokens.createdAt": 0,
          "access_tokens.updatedAt": 0,
        })
        .project({
          "permissions.__v": 0,
          "permissions._id": 0,
          "permissions.createdAt": 0,
          "permissions.updatedAt": 0,
        })
        .project({
          "roles.__v": 0,
          "roles._id": 0,
          "roles.createdAt": 0,
          "roles.updatedAt": 0,
        })
        .project({
          "groups.__v": 0,
          "groups._id": 0,
          "groups.createdAt": 0,
          "groups.updatedAt": 0,
        })
        .skip(skip ? skip : 0)
        .limit(limit ? limit : 100)
        .allowDiskUse(true);
      if (!isEmpty(response)) {
        let data = response;
        return {
          success: true,
          message: "successfully retrieved the user details",
          data,
          status: HTTPStatus.OK,
        };
      } else if (isEmpty(users)) {
        return {
          success: true,
          message: "no users exist",
          data: [],
          status: HTTPStatus.NOT_FOUND,
        };
      }
    } catch (error) {
      logObject("error", error);
      return {
        success: false,
        message: "Internal Server Error",
        errors: { message: error.message },
        status: HTTPStatus.INTERNAL_SERVER_ERROR,
      };
    }
  },

  async modify({ filter = {}, update = {} } = {}) {
    try {
      let options = { new: true };
      let modifiedUpdate = update;
      modifiedUpdate["$addToSet"] = {};

      if (update.password) {
        modifiedUpdate.password = bcrypt.hashSync(update.password, saltRounds);
      }

      if (modifiedUpdate.networks) {
        modifiedUpdate["$addToSet"]["networks"] = {};
        modifiedUpdate["$addToSet"]["networks"]["$each"] =
          modifiedUpdate.networks;
        delete modifiedUpdate["networks"];
      }

      if (modifiedUpdate.permissions) {
        modifiedUpdate["$addToSet"]["permissions"] = {};
        modifiedUpdate["$addToSet"]["permissions"]["$each"] =
          modifiedUpdate.permissions;
        delete modifiedUpdate["permissions"];
      }

      if (modifiedUpdate.roles) {
        modifiedUpdate["$addToSet"]["roles"] = {};
        modifiedUpdate["$addToSet"]["roles"]["$each"] = modifiedUpdate.roles;
        delete modifiedUpdate["roles"];
      }

      if (modifiedUpdate.groups) {
        modifiedUpdate["$addToSet"]["groups"] = {};
        modifiedUpdate["$addToSet"]["groups"]["$each"] = modifiedUpdate.groups;
        delete modifiedUpdate["groups"];
      }

      let updatedUser = await this.findOneAndUpdate(
        filter,
        modifiedUpdate,
        options
      ).exec();
      if (!isEmpty(updatedUser)) {
        let data = updatedUser._doc;
        return {
          success: true,
          message: "successfully modified the user",
          data,
        };
      } else {
        return {
          success: false,
          message: "user does not exist, please crosscheck",
        };
      }
    } catch (error) {
      return {
        success: false,
        message: "User model server error - modify",
        error: error.message,
      };
    }
  },
  async remove({ filter = {} } = {}) {
    try {
      let options = {
        projection: { _id: 0, email: 1, firstName: 1, lastName: 1 },
      };
      let removedUser = await this.findOneAndRemove(filter, options).exec();

      if (!isEmpty(removedUser)) {
        let data = removedUser._doc;
        return {
          success: true,
          message: "successfully removed the user",
          data,
          status: HTTPStatus.OK,
        };
      } else {
        return {
          success: false,
          message: "user does not exist, please crosscheck",
          status: HTTPStatus.NOT_FOUND,
        };
      }
    } catch (error) {
      return {
        success: false,
        message: "User model server error - remove",
        error: error.message,
        status: HTTPStatus.INTERNAL_SERVER_ERROR,
      };
    }
  },
};

UserSchema.methods = {
  authenticateUser(password) {
    return bcrypt.compareSync(password, this.password);
  },
  createToken() {
    return jwt.sign(
      {
        _id: this._id,
        locationCount: this.locationCount,
        organization: this.organization,
        long_organization: this.long_organization,
        firstName: this.firstName,
        lastName: this.lastName,
        userName: this.userName,
        email: this.email,
        privilege: this.privilege,
        profilePicture: this.profilePicture,
        phoneNumber: this.phoneNumber,
      },
      constants.JWT_SECRET
    );
  },
  newToken() {
    const token = accessCodeGenerator.generate(
      constants.RANDOM_PASSWORD_CONFIGURATION(10)
    );
    const hashedToken = bcrypt.hashSync(token, saltRounds);
    return {
      accessToken: hashedToken,
      plainTextToken: `${token.id}|${plainTextToken}`,
    };
  },
  toAuthJSON() {
    return {
      _id: this._id,
      userName: this.userName,
      token: `JWT ${this.createToken()}`,
      email: this.email,
    };
  },
  toJSON() {
    return {
      _id: this._id,
      userName: this.userName,
      email: this.email,
      firstName: this.firstName,
      lastName: this.lastName,
      locationCount: this.locationCount,
      privilege: this.privilege,
      website: this.website,
      organization: this.organization,
      long_organization: this.long_organization,
      category: this.category,
      jobTitle: this.jobTitle,
      profilePicture: this.profilePicture,
      phoneNumber: this.phoneNumber,
      description: this.description,
      createdAt: this.createdAt,
      updatedAt: this.updatedAt,
    };
  },
};

/***
 * prototype functions need to be added here
 */
const User = {
  prototype: {},
};

User.prototype.newToken = async function newToken(device_name = "Web FE") {
  const plainTextToken = Random(40);

  const token = await this.createToken({
    name: device_name,
    token: hash(plainTextToken),
  });

  return {
    accessToken: token,
    plainTextToken: `${token.id}|${plainTextToken}`,
  };
};

User.prototype.hasRole = async function hasRole(role) {
  if (!role || role === "undefined") {
    return false;
  }
  const roles = await this.getRoles();
  return !!roles.map(({ name }) => name).includes(role);
};

User.prototype.hasPermission = async function hasPermission(permission) {
  if (!permission || permission === "undefined") {
    return false;
  }
  const permissions = await this.getPermissions();
  return !!permissions.map(({ name }) => name).includes(permission.name);
};

User.prototype.hasPermissionThroughRole =
  async function hasPermissionThroughRole(permission) {
    if (!permission || permission === "undefined") {
      return false;
    }
    const roles = await this.getRoles();
    // eslint-disable-next-line no-restricted-syntax
    for await (const item of permission.roles) {
      if (roles.filter((role) => role.name === item.name).length > 0) {
        return true;
      }
    }
    return false;
  };

User.prototype.hasPermissionTo = async function hasPermissionTo(permission) {
  if (!permission || permission === "undefined") {
    return false;
  }
  return (
    (await this.hasPermissionThroughRole(permission)) ||
    this.hasPermission(permission)
  );
};

module.exports = UserSchema;
