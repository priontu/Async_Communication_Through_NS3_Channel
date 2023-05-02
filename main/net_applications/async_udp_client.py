from Network.Common.Protocols.Async_UDP_App import UDPClient
from Network.Common.Connection_Definitions import Bind_Info

if __name__=="__main__":
    bind = Bind_Info()
    host = bind.server
    port = bind.port
    udp_cl = UDPClient()
    udp_cl.run_client(host = host, port = port)