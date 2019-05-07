const path = require('path');
const webpack = require('webpack');

module.exports = {
  entry: './js/main.js',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'main.js'
  },
  plugins: [
      new webpack.ProvidePlugin({
          "$": "jquery",
          "m": "mithril",
      }),
  ],
};