import socket
import argparse

class Bind_Info:
    def __init__(self, server = None, port = None, num_packs = None) -> None:
        SERVER, PORT, NUM_PACKS = self.take_input()    
        self.server = SERVER
        self.port = PORT
        self.num_packets = NUM_PACKS

    def set_server(self, server):
        self.server = server

    def set_port(self, port):
        self.port = port

    def take_input(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--host', type=str, required=True)
        parser.add_argument('--port', type=int, required=True)
        parser.add_argument('--num_packets', type=int, required=False)
        args = parser.parse_args()
        print(args)
        host = args.host
        port = args.port
        num_packets = args.num_packets
        return host, port, num_packets


    def print_bind_info(self):
        print("SERVER: ", self.server)
        print("PORT: ", self.port)

if __name__=='__main__':
    Bind_Info()

