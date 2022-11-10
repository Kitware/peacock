const rpc = require('vscode-ws-jsonrpc')
const server = require('vscode-ws-jsonrpc/lib/server')
const lsp = require('vscode-languageserver')

const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 8989 });

const args = process.argv
if (args.length < 3) {
  console.log("Please provide path to server exe")
  throw new Error()
}

const server_path = process.argv[2]

function launch (socket) {
  const reader = new rpc.WebSocketMessageReader(socket)
  const writer = new rpc.WebSocketMessageWriter(socket)
  const socketConnection = server.createConnection(reader, writer, () => socket.dispose())
  const serverConnection = server.createServerProcess('JSON', 'node', [server_path, '--stdio'])
  server.forward(socketConnection, serverConnection, message => {
    console.log(message)
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