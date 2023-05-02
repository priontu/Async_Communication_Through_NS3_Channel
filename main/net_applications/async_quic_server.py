from Network.Common.Protocols.Async_QUIC_App import QuicServer
from Network.Common.Connection_Definitions import Bind_Info

if __name__=="__main__":
    bind = Bind_Info()
    host = bind.server
    port = bind.port
    quic_serv = QuicServer(host=host, port=port)
    quic_serv.run_server()