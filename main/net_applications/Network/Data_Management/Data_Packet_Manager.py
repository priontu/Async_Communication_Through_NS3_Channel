from datetime import datetime
from Network.Data_Management.Data_Packet import Data_Packet, Fast_Block, Slow_Block
from Network.Data_Management.Data_Collection import Data_Collection_Manager as DCM
import sys
import pickle
import random

class DPM:
    def __init__(self, dp: Data_Packet = Data_Packet(), expected_to_send = 1000) -> None:
        self.dp = dp        # Data Packet
        self.fast_block: Fast_Block = self.create_fast_block()  # Fast blocks sent every time
        self.slow_block: Slow_Block = self.dp.Slow_Block if self.dp != None else None   # Slow blocks are sent round robin

        self.id_count = -1
        self.received_packet_count = 0
        self.sent_packet_count = 0
        self.data_string = pickle.dumps(self.dp) if self.dp is not None else None
        self.sent_slow_block_tracker = self.create_slow_blocks()    # Keeping a record
        self.received_slow_block_tally = set()
        self.slow_block_count = 0

        self.all_packets_sent = list()
        self.all_received_packets = list()

        self.expected_count = expected_to_send
        if self.dp != None:
            if self.dp.Expected_Count != None:
                self.dp.Expected_Count = self.expected_count

        self.dcm = DCM()

    def create_fast_block(self):
        block = Fast_Block()
        # block.Fast_Block_ID = 0
        # block.Content = [None]*2
        block.Block_Size = len(pickle.dumps(block))
        block.Block_Size = len(pickle.dumps(block))
        # self.dp.Fast_Block = block
        return block
    
    def create_slow_blocks(self):
        blocks = list()
        for i in range(0, 7):
            block = Slow_Block()
            block.Slow_Block_ID = i
            # block.Content = [None]*20
            block.Block_Size = len(pickle.dumps(block))
            block.Block_Size = len(pickle.dumps(block))
            blocks.append(block)
        return blocks

    def print_fast_block_attributes(self):
        # print(f"Fast Block ID: {self.dp.Fast_Block.Fast_Block_ID}")
        # print(f"Fast Block Content {self.dp.Fast_Block.fast_block.Content}")
        print(f"Fast Block Size: {self.dp.Fast_Block.Block_Size}")
    
    def print_slow_block_attributes(self):
        print(f"Slow Block ID: {self.dp.Slow_Block.Slow_Block_ID}")
        # print(f"Slow Block Content: {self.dp.Slow_Block.Content}")
        print(f"Slow Block Size: {self.dp.Slow_Block.Block_Size}")

    
    
    def check_setting(self, source = "Source Unknown"):
        if type(self.dp) is not Data_Packet:
            print(f"{source}: Incorrect Input -- Provide Object of Type: Data_Packet.")
            quit()
    
    def set_dp(self, dp: Data_Packet):
        self.dp = dp
        self.fast_block = self.dp.Fast_Block
        self.slow_block = self.dp.Slow_Block

    def get_dp(self):
        return self.dp
        
    def increment_ID(self):
        self.check_setting(source = "increment_ID")
        self.id_count += 1
        self.dp.Packet_ID = self.id_count
        return self.dp.Packet_ID
        
    def record_send_time(self):
        self.check_setting(source = "record_send_time")
        self.dp.Send_Time = datetime.now()
        return self.dp.Send_Time
        
    def record_receive_time(self):
        self.check_setting(source = "record_receive_time")
        self.dp.Receive_Time = datetime.now()
        return self.dp.Receive_Time
        
    def calculate_delay(self):
        self.check_setting(source = "calculate_delay")
        if (self.dp.Receive_Time is None):
            print("Error: Receive Time Not Set!")
            quit()
        if (self.dp.Send_Time == None):
            print("Error: Send time Not Set!")
            quit()
        self.dp.Detected_Delay = self.dp.Receive_Time - self.dp.Send_Time
        return self.dp.Detected_Delay
    
    def set_expected_count(self, count):
        self.expected_count = count
        self.dp.Expected_Count = count
    
    def set_packet_size(self):
        data_string = pickle.dumps(self.dp)
        len_dts = len(data_string)
        len_len_dts = len(pickle.dumps(len_dts))

        self.dp.Packet_Size = len_dts + len_len_dts
    
    def set_sent_packet_count(self):
        self.dp.Sent_Packet_Count = self.sent_packet_count

    def set_received_packet_count(self):
        self.dp.Received_Packet_Count = self.received_packet_count

    def set_dp_content(self):
        self.dp.Content = 0
        
    def prepare_for_send(self, expected_to_send: int = None):
        # self.check_setting()
        self.increment_ID()
        self.record_send_time()
        # self.set_dp_content()
        self.set_dp_content()
        self.dp.Fast_Block = self.fast_block
        self.dp.Slow_Block = self.sent_slow_block_tracker[self.sent_packet_count % 7]
        self.slow_block = self.dp.Slow_Block
        self.slow_block_count += 1
        if expected_to_send is not None: 
            self.set_expected_count(expected_to_send)
        self.sent_packet_count += 1
        self.set_sent_packet_count()
        self.set_packet_size()
        self.all_packets_sent.append(self.dp)
        return self.dp
    
    def prepare_after_receive(self):
        # self.check_setting()
        self.record_receive_time()
        self.calculate_delay()
        self.id_count = self.dp.Packet_ID
        self.received_packet_count += 1
        self.fast_block = self.dp.Fast_Block
        self.slow_block = self.dp.Slow_Block
        self.received_slow_block_tally.add(self.dp.Slow_Block)
        self.set_received_packet_count()
        self.all_received_packets.append(self.dp)
        self.dcm.add_dps(self.dp)
        return self.dp

    def print_attributes(self):
        print("Packet_ID: ", self.dp.Packet_ID)
        print("Send Time: ", self.dp.Send_Time)
        print("Receive Time: ", self.dp.Receive_Time)
        print("Detected Delay: ", self.dp.Detected_Delay)
        print("Sent Packet Count: ", self.dp.Sent_Packet_Count)
        print("Received_Packet_Count: ", self.dp.Received_Packet_Count )
        print("Expected Count: ", self.dp.Expected_Count)
        print("Packet Size: ", self.dp.Packet_Size)
        print("Buffer_Push_Time: ", self.dp.Buffer_Push_Time)
        print("Buffer_Pop_Time: ", self.dp.Buffer_Pop_Time)
        print("Buffer_Time_Difference", self.dp.Buffer_Time_Difference)
        print("Content: ", self.dp.Content)
        # print("Content: ", self.dp.Content)
        self.print_fast_block_attributes()
        self.print_slow_block_attributes()
        print(" ")
    


        
        
    
    
        
    
        
    
