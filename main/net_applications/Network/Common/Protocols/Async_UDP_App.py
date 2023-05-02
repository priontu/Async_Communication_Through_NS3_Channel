import asyncio
from asyncio.protocols import DatagramProtocol
from Network.Data_Management.Data_Packet_Manager import Data_Packet
from Network.Data_Management.Data_Packet_Manager import DPM
from Network.Data_Management.Buffer import Buffer

import json
import pickle 
import time

class UDPClientProtocol(DatagramProtocol):
	def __init__(self, on_con_lost, host: str, port: int, data = Data_Packet()) -> None:
		self.dp = data
		self.dpm = DPM(self.dp)
		self.buff = Buffer()
		self.data_string = None
		self.on_con_lost = on_con_lost
		self.transport = None
		self.sent_count = 0
		self.host = host
		self.port = port
	
	def connection_made(self, transport):
		self.transport = transport
		print(f"Sending the following to {self.host}/{self.port}:")
		while self.sent_count < self.dp.Expected_Count:
			self.dpm.prepare_for_send()
			self.dpm.print_attributes()
			self.data_string = pickle.dumps(self.dpm.get_dp())
			self.transport.sendto(self.data_string)
			self.sent_count += 1
			# time.sleep(0.01)
		self.transport.close()
	
	def datagram_received(self, data, addr):
		## Processing done here

		self.transport.close()
	
	def error_received(self, exc):
		print('Error received:\n', exc)

	def connection_lost(self, exc):
		print("Connection closed.")
		print('Error received:\n', exc)
		self.on_con_lost.set_result(True)


class UDPClient:
	def __init__(self, host = None, port = None, expected_to_send = 1000) -> None:
		self.data = Data_Packet()
		self.data.Expected_Count = expected_to_send
		self.loop = None
		self.on_con_lost = None
		self.transport = None
		self.protocol = None
		self.host = host
		self.port = port
	
	async def main(self):
		self.loop = asyncio.get_running_loop()
		self.on_con_lost = self.loop.create_future()
		self.transport, self.protocol = await self.loop.create_datagram_endpoint(
			lambda: UDPClientProtocol(host = self.host, port = self.port,data = self.data, on_con_lost = self.on_con_lost),
			remote_addr = (self.host, self.port)
		)

		try:
			await self.on_con_lost
		finally:
			self.transport.close()
	
	def run_client(self, host = None, port = None):
		if (self.host is not None) and (self.port is not None):
			print("Host and Port being changed: ")
			print(f"Previous Host: {self.host}")
			print(f"Prevous Port: {self.port}")
			print(f"New Host: {host}")
			print(f"New Port: {port}")
		self.host = host
		self.port = port
		try:
			asyncio.run(self.main())
		except KeyboardInterrupt:
			pass


class UDPServerProtocol(DatagramProtocol):
	def __init__(self, on_con_lost) -> None:
		self. transport = None
		self.dpm = DPM()
		self.dp = None
		self.on_con_lost = on_con_lost

	def connection_made(self, transport):
		self.transport = transport
		print("UDP Connection Made.")
		print(transport)

	def datagram_received(self, data, addr):
		packet = pickle.loads(data)
		self.dpm.set_dp(packet)
		self.dpm.prepare_after_receive()
		print(f"Received the following from {addr}:\n")
		self.dpm.print_attributes()

		print()
		print("on_con_lost: \n", self.on_con_lost)
		print("is_closing:\n", self.transport.is_closing())
		print()
	
	def error_received(self, exc):
		print('Error received:\n', exc)

	def connection_lost(self, exc):
		print("Connection closed.")
		print('Error received:\n', exc)

		self.dpm.dcm.prepare_all_data()
		self.dpm.dcm.print_attributes()
		self.on_con_lost.set_result(True)

class UDPServer:
	def __init__(self, host = None, port = None, server_run_time: int = None) -> None:
		self.loop = None
		self.run_time = server_run_time
		self.host = host
		self.port = port
	
	async def main(self):
		self.loop = asyncio.get_running_loop()
		self.on_con_lost = self.loop.create_future()
		self.transport, self.protocol = await self.loop.create_datagram_endpoint(
			lambda: UDPServerProtocol(on_con_lost = self.on_con_lost),
			local_addr = (self.host, self.port)
		)

		try: 
			if self.run_time is None:
				await asyncio.Event().wait()	
			else:
				await asyncio.sleep(self.run_time)
		except KeyboardInterrupt:
			self.transport.close()
		finally:
			self.transport.close()
	
	def run_server(self, host = None, port = None):
		if (self.host is not None) and (self.port is not None):
			print("Host and Port being changed: ")
			print(f"Previous Host: {self.host}")
			print(f"Prevous Port: {self.port}")
			print(f"New Host: {host}")
			print(f"New Port: {port}")
		self.host = host
		self.port = port
		try:
			asyncio.run(self.main())
		except KeyboardInterrupt:
			pass
