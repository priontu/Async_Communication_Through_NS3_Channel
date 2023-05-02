from aioquic.asyncio.client import connect
import asyncio
from aioquic.asyncio.server import serve
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic import events
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import QuicEvent, StreamDataReceived, DatagramFrameReceived
from aioquic.quic.logger import QuicFileLogger
from Network.Data_Management.Data_Packet import Data_Packet
from Network.Data_Management.Data_Packet_Manager import DPM
from aioquic.quic.connection import QuicConnection, NetworkAddress
import pickle
from typing import Any, Callable, Dict, Optional, Text, Tuple, Union, cast
import time
from aioquic.quic.packet import QuicErrorCode
from aioquic.tls import SessionTicket, SessionTicketHandler, SessionTicketFetcher
import logging

QuicStreamHandler = Callable[[asyncio.StreamReader, asyncio.StreamWriter], None]
logger = logging.getLogger("client")


global NUM_PACKETS, HOST, PORT

NUM_PACKETS: int = 1000
HOST: str = None
PORT: int = None

class QuicClientProto(QuicConnectionProtocol):
	def __init__(self, quic: QuicConnection, stream_handler: Optional[QuicStreamHandler] = [asyncio.StreamReader, asyncio.StreamWriter]):
		super().__init__(quic, stream_handler)

		global NUM_PACKETS, HOST, PORT
		self.expected_count = NUM_PACKETS
		self.dp = Data_Packet()
		self.dp.Expected_Count = NUM_PACKETS
		self.dpm = DPM(dp = self.dp, expected_to_send = NUM_PACKETS)
		self.send_count = 0
		self.host = HOST
		self.port = PORT
		self.transport = None
	
	def connection_made(self, transport: asyncio.BaseTransport) -> None:
		print("QUIC Connection Made.")
		self.transport = transport
		return super().connection_made(transport)

	async def send_data(self):
		count = 0
		print(f"Sending the following to {self.host}/{self.port}:")
		while self.send_count < self.dp.Expected_Count:
			stream_id = self._quic.get_next_available_stream_id()
			self.dpm.prepare_for_send()
			# self.dpm.dp.Content = 4
			print("Sending the following: ")
			self.dpm.print_attributes()
			data_string = pickle.dumps(self.dpm.get_dp())
			# reader, writer = self._create_stream(stream_id)
			# self._stream_handler(reader, writer)
			# writer.write(data=data_string)
			# if self.send_count % 35 == 0:
			#     stream_id = self._quic.get_next_available_stream_id()               
			print("Stream_ID: ", stream_id)
			self._quic.send_stream_data(stream_id = stream_id,
										data = data_string,
										end_stream = False)
			waiter = self._loop.create_future()
			self._ack_waiter = waiter
			# self._quic.send_datagram_frame(data_string)
			# print(writer)
			self.send_count += 1
			self.transmit()
			# self._quic.reset_stream(stream_id=stream_id, error_code=QuicErrorCode.NO_ERROR)

			self.response = await asyncio.shield(waiter)
			print()
			print("Response:\n", self.response)
			print()
			time.sleep(0.01)
	
	# async def send_datagram(self):
	#     msg = b"Hello World"
	#     self._quic.send_datagram_frame(msg)
	#     self.transmit()
	def connection_lost(self, exc) -> None:
		print("Connection Lost!!")
		print("Error:\n", exc)
		return super().connection_lost(exc)
	
	def quic_event_received(self, event: QuicEvent) -> None:
		print()
		print("Event Received: \n", event)
		if isinstance(event, StreamDataReceived):
			waiter = self._ack_waiter
			self._ack_waiter = None
			waiter.set_result(event.data.decode())

	



	
	
class QuicClient:
	def __init__(self, host: str, port: int, expected_to_send: int = 1000) -> None:
		self.host = host
		self.port = port
		self.expected_count = expected_to_send
		self.protocol = QuicClientProto
		self.configuration = QuicConfiguration(is_client=True)
		# with open("session-tickets.pkl", "rb") as fp:
		#     self.configuration.session_ticket = pickle.load(fp)
		self.configuration.load_verify_locations('cert.pem')
		global NUM_PACKETS, HOST, PORT 
		NUM_PACKETS = expected_to_send
		HOST = self.host
		PORT = self.port
	

	def save_session_ticket(self, ticket: SessionTicket) -> None:
		"""
		Callback which is invoked by the TLS engine when a new session ticket
		is received.
		"""
		logger.info("New session ticket received")
		with open("session-tickets.pkl", "wb") as fp:
				pickle.dump(ticket, fp)

	async def main(self):
		async with connect(
			host = self.host,
			port = self.port,
			configuration = self.configuration,
			create_protocol = self.protocol,
			session_ticket_handler= self.save_session_ticket,
			wait_connected = True
		) as client:
			response = await client.send_data()
			# response_2 = await client.send_datagram()
	
	def run_client(self):
		asyncio.run(
			self.main()
		)

class QuicServerProto(QuicConnectionProtocol):
	def __init__(self, quic: QuicConnection, stream_handler: Optional[QuicStreamHandler] = None):
		super().__init__(quic, stream_handler)
		self.incomplete = 0

	def connection_made(self, transport: asyncio.BaseTransport) -> None:
		print("QUIC Connection Made.")
		return super().connection_made(transport)

	def quic_event_received(self, event):
		self.dp = None
		self.dpm = DPM()
		print("Event:\n", event)

		if isinstance(event, StreamDataReceived):

			data_string = event.data
			self.dp = pickle.loads(data_string)
			self.dpm.set_dp(self.dp)
			print(self.dp)
			self.dpm.prepare_after_receive()
			print("\nPacket data:")
			self.dpm.print_attributes()
			
			ack_msg = f"Received: Packet_ID = {self.dpm.dp.Packet_ID}"
			self._quic.send_stream_data(stream_id=event.stream_id,
										data=ack_msg.encode(),
										end_stream=True)



			
		#     if event.end_stream:
		#         reader.feed_eof()

		#         self.dp = pickle.loads(data_string)
		#         self.dpm.set_dp(self.dp)
		#         print(self.dp)
		#         self.dpm.prepare_after_receive()
		#         print("\nPacket data:")
		#         self.dpm.print_attributes()
		#     else:
		#         print("Incomplete Stream: ")
		#         print(event.data)
		
		if isinstance(event, DatagramFrameReceived):
			print("Datagram Received...")
			print(event)
	
	# def datagram_received(self, data, addr):
	#     print(data)
		
	# def datagram_received(self, data: Union[bytes, Text], addr: NetworkAddress) -> None:
	#     self._quic.receive_datagram(cast(bytes, data), addr, now=self._loop.time())
	#     self._process_events()
	#     self.transmit()
	#     print("address: ", addr)

	#     print(data.decode())

		# if isinstance(event, DatagramFrameReceived):
		#     data_string = event.data
		#     self.dp = pickle.loads(data_string)
		#     self.dpm.set_dp(self.dp)
		#     print(self.dp)
		#     self.dpm.prepare_after_receive()
		#     print("\nPacket data:")
		#     self.dpm.print_attributes()

class SessionTicketStore:
	"""
	Simple in-memory store for session tickets.
	"""

	def __init__(self) -> None:
		self.tickets: Dict[bytes, SessionTicket] = {}

	def add(self, ticket: SessionTicket) -> None:
		self.tickets[ticket.ticket] = ticket

	def pop(self, label: bytes) -> Optional[SessionTicket]:
		return self.tickets.pop(label, None)

class QuicServer:
	def __init__(self, host: str, port: int) -> None:
		self.host = host
		self.port = port
		self.config = QuicConfiguration(is_client=False)
		self.config.load_cert_chain('cert.pem', 'key.pem')
		self.protocol = QuicServerProto
		self.session_ticket_store = SessionTicketStore()
	
	async def main(self):
		await serve(host=self.host,
					port=self.port,
					configuration=self.config,
					create_protocol=QuicServerProto,
					session_ticket_fetcher = self.session_ticket_store.pop,
					session_ticket_handler = self.session_ticket_store.add,
					retry = True
					)
		await asyncio.Future()

	def run_server(self):
		try:
			asyncio.run(self.main())
		except KeyboardInterrupt:
			pass
		

