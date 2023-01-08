const generatePassword = require("generate-password");
const constants = require("../config/constants");
const log4js = require("log4js");
const logger = log4js.getLogger(
  `${constants.ENVIRONMENT} -- generate-password-util`
);

const createPassword = (length) => {
  try {
    let password = generatePassword.generate(
      constants.RANDOM_PASSWORD_CONFIGURATION(length)
    );
    return {
      success: true,
      message: "password generated",
      data: password,
    };
  } catch (e) {
    logElement("generate password util error message", e.message);
    return {
      success: false,
      message: "generate password util server error",
      error: e.message,
    };
  }
};

module.exports = createPassword;
