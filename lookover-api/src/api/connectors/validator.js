const Joi = require('joi');

const createConnectionValidator = Joi.object({
    name: Joi.string().required(),
    plugin: Joi.string().required()
});

