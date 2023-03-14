import 'xterm/css/xterm.css';
import { Terminal } from 'xterm';

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
      let rowHeight = 17;
      let numRows = Math.floor(this.$el.clientHeight / rowHeight);
      this.term.resize(this.term.cols, numRows);
    };

    this.resizeObserver = new ResizeObserver(this.onResize);

    this.term = new Terminal();
    this.term.open(this.$el);
    this.resizeObserver.observe(this.$el);
  },
  beforeDestroy() {
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
      this.resizeObserver = null;
    }
  },
};
