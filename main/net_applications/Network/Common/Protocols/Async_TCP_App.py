import asyncio
from Network.Data_Management.Data_Packet import Data_Packet
from Network.Data_Management.Data_Packet_Manager import DPM
import pickle
import time

class TCPClientProtocol(asyncio.Protocol):
	def __init__(self, host: str, port: int, on_con_lost, data = Data_Packet()):
		self.dp = data
		self.dpm = DPM(self.dp)
		self.on_con_lost = on_con_lost
		self.host = host
		self.port = port
		self.transport = None
		self.sent_count = 0
		self.data_string = None
	
	def connection_made(self, transport):
		self.transport = transport
		print(f"Sending the following to {self.host}/{self.port}:")
		while self.sent_count < self.dp.Expected_Count:
			self.dpm.prepare_for_send()
			self.dpm.print_attributes()
			self.data_string = pickle.dumps(self.dpm.get_dp())
			self.transport.write(self.data_string)
			time.sleep(1)
			self.sent_count += 1
		transport.close()

	def data_received(self, data: bytes):
		self.dp = pickle.loads(data)
		self.dpm.set_dp(self.dp)
		print("The following package is received: ")
		self.dpm.print_attributes()
	
	def connection_lost(self, exc: Exception | None):
		print("The server closed the connection.")
		self.on_con_lost.set_result(True)

class TCPClient:
	def __init__(self, host: str = None, port: int = None, expected_to_send = 1000 ) -> None:
		self.loop = None
		self.on_con_lost = None
		self.dp = Data_Packet()
		self.dp.Expected_Count = expected_to_send
		self.transport = None
		self.protocol = None
		self.host = host
		self.port = port
	
	async def main(self):
		self.loop = asyncio.get_running_loop()
		self.on_con_lost = self.loop.create_future()
		self.transport, self.protocol = await self.loop.create_connection(
			lambda: TCPClientProtocol(data = self.dp, on_con_lost = self.on_con_lost, host = self.host, port = self.port),
			host = self.host,
			port = self.port
		)
		try:
			await self.on_con_lost
		finally:
			self.transport.close()
	def run_client(self):
		asyncio.run(self.main())

class TCPServerProtocol(asyncio.Protocol):
	def __init__(self) -> None:
		self. transport = None
		self.dpm = DPM()
		self.dp = None
		self.peername = None

	def connection_made(self, transport):
		self.transport = transport
		self.peername = self.transport.get_extra_info("peername")
		print(f"TCP Connection made with {self.peername}")
	
	def data_received(self, data_string):
		self.dp = pickle.loads(data_string)
		self.dpm.set_dp(self.dp)
		self.dpm.prepare_after_receive()
		print(f"The following data packet has been received from {self.peername}: ")
		self.dpm.print_attributes()
	

class TCPServer:
	def __init__(self, host: str = None, port: int = None) -> None:
		self.host = host
		self.port = port
		self.loop = None

	async def main(self):
		self.loop = asyncio.get_running_loop()
		server = await self.loop.create_server(
			lambda: TCPServerProtocol(),
			host = self.host,
			port = self.port
		)
		
		try:
			async with server:
				await server.serve_forever()
		except KeyboardInterrupt:
			pass
	
	def run_server(self):
		asyncio.run(self.main())



