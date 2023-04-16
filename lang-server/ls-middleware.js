const rpc = require('vscode-ws-jsonrpc')
const server = require('vscode-ws-jsonrpc/lib/server')
const lsp = require('vscode-languageserver')

const WebSocket = require('ws');

const args = process.argv
if (args.length < 4) {
  console.log("Usage: node ls-middleware.js server_path port")
  throw new Error()
}

const server_path = process.argv[2]
const port = process.argv[3]

const wss = new WebSocket.Server({ port: port });

function launch (socket) {
  const reader = new rpc.WebSocketMessageReader(socket)
  const writer = new rpc.WebSocketMessageWriter(socket)
  const socketConnection = server.createConnection(reader, writer, () => socket.dispose())
  const serverConnection = server.createServerProcess('JSON', 'node', [server_path, '--stdio'])
  server.forward(socketConnection, serverConnection, message => {
    // console.log(message)
    if (message.method == 'serverDebugNotification') {
      // server debug messages are huge and slow down the editor
      // we don't use them for any functionality so we will ignore them for now
      return null
    }
    if (rpc.isRequestMessage(message)) {
      if (message.method === lsp.InitializeRequest.type.method) {
        const initializeParams = message.params
        initializeParams.processId = process.pid
      }
    }
    return message
  })
}

wss.on('connection', function connection(ws) {
  const socket = {
    send:(content)=>ws.send(content,(error)=>{
      if(error){
        console.log(error)
      }
    }),
    onMessage:(cb)=>ws.on('message',cb),
    onError:(cb)=>ws.on('error',cb),
    onClose:(cb)=>ws.on('close',cb),
    dispose:(cb)=>ws.close()
  }
  launch(socket)
})