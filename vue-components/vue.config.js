const path = require('path');
const DST_PATH = '../peacock_trame/module/serve';
const MonacoWebpackPlugin = require('monaco-editor-webpack-plugin')

module.exports = {
  configureWebpack: {
      
    plugins: [
      new MonacoWebpackPlugin({
        languages: []
      }),
    ]
  },
  chainWebpack: (config) => {
    config.resolve.alias.set(
      "vscode",
      path.resolve(
        "./node_modules/monaco-languageclient/lib/vscode-compatibility"
      )
    );
  },
  outputDir: path.resolve(__dirname, DST_PATH),
};
