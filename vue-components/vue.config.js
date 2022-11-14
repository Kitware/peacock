const path = require('path');
const DST_PATH = '../peacock_trame/module/serve';
const MonacoWebpackPlugin = require('monaco-editor-webpack-plugin')
const CopyPlugin = require("copy-webpack-plugin");

module.exports = {
  configureWebpack: {
    plugins: [
      new MonacoWebpackPlugin({
        languages: []
      }),

      new CopyPlugin({
        patterns: [
          {
            from: "node_modules/vscode-oniguruma/release/onig.wasm",
            to: path.resolve(__dirname, DST_PATH),
          },
        ]
      })
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
