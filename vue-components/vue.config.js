const path = require('path');
const DST_PATH = '../peacock_trame/module/serve';
const MonacoWebpackPlugin = require('monaco-editor-webpack-plugin')

module.exports = {
  configureWebpack: {
      
    plugins: [
      new MonacoWebpackPlugin({
        languages: ['plaintext']
      })
    ]
  },
  outputDir: path.resolve(__dirname, DST_PATH),
};
