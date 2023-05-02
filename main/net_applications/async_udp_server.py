from Network.Common.Protocols.Async_UDP_App import UDPServer
from Network.Common.Connection_Definitions import Bind_Info

if __name__=="__main__":
    bind = Bind_Info()
    host = bind.server
    port = bind.port
    udp_serv = UDPServer()
    udp_serv.run_server(host = host, port = port)