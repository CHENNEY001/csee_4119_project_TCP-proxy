The TCP proxy is implemented in this directory.

You can execute the proxy server by following commands:

`cd ~/csee_4119_abr_project/proxy`

`./proxy <log> <alpha> <listen-port> <fake-ip> <web-server-ip>`

alpha: A float in the range [0,1]. This is the coefficient in your EWMA throughput estimate.

listen-port: The TCP port used to listen on for accepting connections from your browser. 

fake-ip: Your proxy will bind to this IP address for outbound connections to the web servers. The fake-ip can only be one of the clients’ IP addresses under the network topology you specified (see Network Simulation). If we bind the outbound socket to this fake-ip, then we can be sure that packets sent between the proxy and the server traverse ONLY the links set by netsim. (and here is why you want your packets to traverse netsim links only)

web-server-ip: Your proxy will accept an argument specifying the IP address of the web server from which it should request video chunks. It can only be one of the servers’ IP addresses under the network topology you specified (see Network Simulation).
