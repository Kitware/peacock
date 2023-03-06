import 'xterm/css/xterm.css';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';

export default {
  name: 'Terminal',
  methods: {
    write(string) {
      this.term.writeln(string);
    },
    clear() {
      this.term.clear();
    },
  },
  mounted() {
    this.onResize = () => {
      this.fitAddon.fit();
    };

    this.resizeObserver = new ResizeObserver(this.onResize);

    this.term = new Terminal();
    this.fitAddon = new FitAddon();
    this.term.loadAddon(this.fitAddon);
    this.term.open(this.$el);
    this.fitAddon.fit();
    this.resizeObserver.observe(this.term.element);
  },
  beforeDestroy() {
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
      this.resizeObserver = null;
    }
  },
};
