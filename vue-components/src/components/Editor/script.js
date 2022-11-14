import {
  MonacoLanguageClient,
  CloseAction,
  ErrorAction,
  createConnection,
  MonacoServices,
} from "monaco-languageclient";
import { listen } from 'vscode-ws-jsonrpc';

// import * as monaco from 'monaco-editor/esm/vs/editor/editor.api';
import loader from "@monaco-editor/loader";

import {createOnigScanner, createOnigString, loadWASM} from 'vscode-oniguruma';
import {SimpleLanguageInfoProvider} from './lib/providers';
import {registerLanguages} from './lib/register';
import {rehydrateRegexps} from './lib/configuration';
import VsCodeDarkTheme from './lib/vs-dark-plus-theme';

import moose_config from './assets/moose_config.json'
import moose_grammar from './assets/moose_grammar.json'

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
    async loadVSCodeOnigurumWASM() {
      const response = await fetch('__peacock_trame/onig.wasm');
      const contentType = response.headers.get('content-type');
      if (contentType === 'application/wasm') {
          return response;
      }
      // Using the response directly only works if the server sets the MIME type 'application/wasm'.
      // Otherwise, a TypeError is thrown when using the streaming compiler.
      // We therefore use the non-streaming compiler :(.
      return await response.arrayBuffer();
    }
  },
  mounted() {
    loader.init().then(async (monaco) => {
      const languages = [
        {
          id: 'moose',
          extensions: [
              '.i',
          ],
          aliases: ['Moose'],
          filenames: [],
          firstLine: '',
        }
      ];
      const grammars = {
        'input.moose': {
          language: 'moose',
          path: 'moose.json',
        }
      };
      const fetchGrammar = async (scopeName) => {
        const { path } = grammars[scopeName];
        // const uri = `/grammars/${path}`;
        // const response = await fetch(uri);
        // const grammar = await response.text();
        const grammar = JSON.stringify(moose_grammar)
        const type = path.endsWith('.json') ? 'json' : 'plist';
        return { type, grammar };
      };
      const fetchConfiguration = async () => {
        // const uri = `/configurations/${language}.json`;
        // const response = await fetch(uri);
        // const rawConfiguration = await response.text();
        const rawConfiguration = JSON.stringify(moose_config)
        return rehydrateRegexps(rawConfiguration);
      };
      const data = await this.loadVSCodeOnigurumWASM();
      await loadWASM(data);
      const onigLib = Promise.resolve({
        createOnigScanner,
        createOnigString,
      });
      const provider = await new SimpleLanguageInfoProvider({
        grammars,
        fetchGrammar,
        configurations: languages.map((language) => language.id),
        fetchConfiguration,
        theme: VsCodeDarkTheme,
        onigLib,
        monaco,
      });
      registerLanguages(languages, (language) => provider.fetchLanguageInfo(language), monaco);

      this.editor = monaco.editor.create(document.getElementById("container"),
        {
          model: monaco.editor.createModel(this.contents, 'moose', monaco.Uri.parse("file://" + this.filepath)),
          theme: 'vs-dark',
          automaticLayout: true,
        }
      )
      provider.injectCSS();

      MonacoServices.install(monaco);
      this.connectToLangServer();

      this.editor.onDidChangeModelContent(() => this.$emit('change', this.editor.getValue()));
    })
  },
};