from Network.Common.Protocols.Async_TCP_App import TCPServer
from Network.Common.Connection_Definitions import Bind_Info

if __name__=="__main__":
    bind = Bind_Info()
    host = bind.server
    port = bind.port
    tcp_serv = TCPServer(host = host, port = port)
    tcp_serv.run_server()