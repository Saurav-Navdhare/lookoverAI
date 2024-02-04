// require('dotenv').config();
const app = require('./app');
const port = process.env.API_PORT;
app.listen(port, () => {
  /* eslint-disable no-console */
  console.log(`Listening: http://localhost:${port}`);
  /* eslint-enable no-console */
});