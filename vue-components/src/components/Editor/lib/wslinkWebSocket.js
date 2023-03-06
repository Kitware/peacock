export class WSLinkWebSocket {
  constructor(trame) {
    this.trame = trame;
    this.isopen = false;

    this.trame.client
      .getConnection()
      .getSession()
      .subscribe('trame.lang.server', ([event]) => {
        // console.log("LINK Event: ", event.type)
        if (event.type == 'close') {
          if (this.onclose) {
            this.onclose({
              code: event.code,
              reason: event.reason,
              type: 'close',
            });
          }
        } else if (event.type == 'message') {
          this.onmessage({ data: event.data });
        } else if (event.type == 'error') {
          if (this.onerror) {
            this.onerror();
          }
        } else if (event.type == 'open') {
          if (this.onopen) {
            this.isopen = true;
            this.onopen();
          }
        }
      });
  }

  connectToLangServer() {
    if (!this.isopen) {
      this.onopen();
    }
  }

  close(code, reason) {
    // console.log("close", code, reason)
    this.trame.trigger('trame_lang_server', ['close', { code, reason }]);
  }

  send(data) {
    // console.log("send", data)
    this.trame.trigger('trame_lang_server', ['send', data]);
  }
}
