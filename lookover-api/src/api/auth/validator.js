const Joi = require("joi");

module.exports.emailValidator = Joi.object({
    email: Joi.string().email().required(),
});

module.exports.orgValidator = Joi.object({
    user_name: Joi.string().required().min(3).max(30).required(),
    user_email: Joi.string().email().required(),
    org_name: Joi.string().min(3).max(30).required(),
    org_description: Joi.string().max(100),
    links: Joi.object(),
    profile_type: Joi.string().valid("individual", "organization").required() 
});

module.exports.signInUpValidator = Joi.object({
    user_name: Joi.string().required().min(3).max(30).required(),
    org_id: Joi.string().required()
});

module.exports.consumeValidator = Joi.object({
    context_id: Joi.string().required(),
    device_id: Joi.string().required(),
    code: Joi.string().required().length(6)
});