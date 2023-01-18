The `proxy` is the executable proxy program, `TCPserver.py` and `TCPclient.py` are test file.

provide parameter for `proxy.py` in this format: `./proxy <listen-port> <fake-ip> <server-ip>`

To test the proxy, you should run `TCPserver.py` firstly, then run `proxy.py` with parameters, lastly you run `TCPclient.py` with parameters.

You need provide parameters for `TCPclient.py` in this format: `./client.py <prox-port> <proxy-ip>`

When connection is established, the client and server can sent messages interactively, the End Of Message (EOM) is the new line character `'\n'`

Client can end the connection by inputting `"exit"`

If a client connects to proxy , the proxy connects to the server. If the client disconnects with proxy, the proxy disconnects with the server

the proxy can buffer 5 clients at most.