import * as monaco from 'monaco-editor'
export default {
  name: "Editor",
  props: ['contents'],
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
  mounted() {
    this.editor = monaco.editor.create(document.getElementById('container'), {
      value: this.contents,
      language: 'plaintext',
    });

    this.editor.onDidChangeModelContent(() => this.$emit('change', this.editor.getValue()));
  },
};