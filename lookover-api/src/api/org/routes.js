const express = require('express')
const router = express.Router();
const controllers = require('./controllers.js');
const verify_session = require('../../middlewares/verify_session');

// Check Routes
router.get('/',(req,res) => {
    return res.send({
        message: "ORG API is working fine."
    })
});

// Org Routes
router.get('/info',verify_session(["org:info"]),controllers.getOrgInfo);


module.exports = router;

