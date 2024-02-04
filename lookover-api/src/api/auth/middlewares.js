const validator = require('./validator');

module.exports.emailValidator = (req, res, next) => {
    try {
        validator.emailValidator(req.body);
        return next();
    } catch (error) {
        if(error.Joi === true) return res.status(403).json({error: error.message});
        else return res.status(500).json({error: error.message});
    }
}

module.exports.orgValidator = (req, res, next) => {
    org = req.body;
    try {
        validator.orgValidator(req.body);
        return next();
    } catch (error) {
        if(error.Joi === true) return res.status(403).json({error: error.message});
        else return res.status(500).json({error: error.message});
    }
}

module.exports.signInUpValidator = (req, res, next) => {
    try {
        validator.signInUpValidator(req.body);
        return next();
    } catch (error) {
        if(error.Joi === true) return res.status(403).json({error: error.message});
        else return res.status(500).json({error: error.message});
    }
}

module.exports.consumeValidator = (req, res, next) => {
    try {
        validator.consumeValidator(req.body);
        return next();
    } catch (error) {
        if(error.Joi === true) return res.status(403).json({error: error.message});
        else return res.status(500).json({error: error.message});
    }
}