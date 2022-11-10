import {
  MonacoLanguageClient,
  CloseAction,
  ErrorAction,
  createConnection,
  MonacoServices,
} from "monaco-languageclient";
import { listen } from 'vscode-ws-jsonrpc';

import loader from "@monaco-editor/loader";

window.setImmediate = window.setTimeout; 

export default {
  name: "Editor",
  props: ['contents', 'filepath'],
  watch: {
    contents(contents) {
      this.editor.setValue(contents)
    }
  },
  data() {
    return {
      editor: undefined,
      options: {
        //Monaco Editor Options
      }
    }
  },
  methods: {
    createLanguageClient: function (connection) {

      return new MonacoLanguageClient({
        name: "Monaco language client",
        clientOptions: {
          documentSelector: ["moose"],
          errorHandler: {
            error: () => ErrorAction.Continue,
            closed: () => CloseAction.Restart,
          },
        },

        connectionProvider: {
          get: (errorHandler, closeHandler) => {
            return Promise.resolve(
              createConnection(connection, errorHandler, closeHandler)
            );
          },
        },
      });
    },
    connectToLangServer: function () {
      const webSocket = new WebSocket("ws://127.0.0.1:8989");

      listen({
        webSocket: webSocket,
        onConnection: (connection) => {
          var languageClient = this.createLanguageClient(connection);
          var disposable = languageClient.start();

          connection.onClose(function () {
            return disposable.dispose();
          });
          
          connection.onError(function (error) {
            console.log(error);
          });

        },
      });
    },
  },
  mounted() {
    loader.init().then((monaco) => {
      monaco.languages.register({id: 'moose'})
      this.editor = monaco.editor.create(document.getElementById("container"),
        {
          model: monaco.editor.createModel(this.contents, 'moose', monaco.Uri.parse("file://" + this.filepath))
        }
      )

      MonacoServices.install(monaco);
      this.connectToLangServer();

      this.editor.onDidChangeModelContent(() => this.$emit('change', this.editor.getValue()));
    })
  },
};