from Network.Common.Protocols.Async_QUIC_App import QuicClient
from Network.Common.Connection_Definitions import Bind_Info

if __name__=="__main__":
    bind = Bind_Info()
    host = bind.server
    port = bind.port
    num_packs = bind.num_packets
    quic_cl = QuicClient(host = host, port = port, expected_to_send=num_packs)
    quic_cl.run_client()