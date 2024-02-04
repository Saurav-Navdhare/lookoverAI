require('dotenv').config();
const express = require('express');
const cors = require('cors');
require('./init/firebase.js');
const app = express();

// Middleware
app.use(express.json())
app.use(cors());
app.use((req, res, next) => {
  req.session = {
    user: null
  };
  next();
});

// Routes
app.get('/', (req, res) => {
    return res.json({
      message: 'Hope youre getting this message'
    });
});


app.use('/auth', require('./api/auth/routes.js'));
app.use('/org', require('./api/org/routes.js'));
app.use('/org/connectors', require('./api/connectors/routes.js'));
app.use('/roles', require('./api/role/routes.js'));
app.use('/org/user', require('./api/user/routes.js'));



module.exports = app;





