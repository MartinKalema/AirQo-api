const constants = require("@config/constants");
const log4js = require("log4js");
const logger = log4js.getLogger(
    `${constants.ENVIRONMENT} -- create-health-tip-util`
);
const httpStatus = require("http-status");
const { Translate } = require('@google-cloud/translate').v2;

const translate = new Translate();

const translateUtil = {
    translate: async (healthTips, targetLanguage) => {
        try {
            const translatedHealthTips = [];

            for (const healthTip of healthTips) {
                const translatedTip = { ...healthTip };
                translatedTip.title = await translateText(healthTip.title, targetLanguage);
                translatedTip.description = await translateText(healthTip.description, targetLanguage);

                translatedHealthTips.push(translatedTip);
            }

            return translatedHealthTips;
        } catch (error) {
            logger.error(`internal server error -- ${error.message}`);
            return {
                success: false,
                message: "Internal Server Error",
                status: httpStatus.INTERNAL_SERVER_ERROR,
                errors: {
                    message: error.message,
                },
            };
        }
    },
};

async function translateText(text, target) {
    try {
        let [translations] = await translate.translate(text, target);
        translations = Array.isArray(translations) ? translations : [translations];
        return translations[0];
    } catch (error) {
        logger.error(`internal server error -- ${error.message}`);
        throw error;
    }
}

module.exports = translateUtil;