from Network.Common.Protocols.Async_TCP_App import TCPClient

from Network.Common.Connection_Definitions import Bind_Info

if __name__=="__main__":
    bind = Bind_Info()
    host = bind.server
    port = bind.port
    tcp_cl = TCPClient(host=host, port = port)
    tcp_cl.run_client()