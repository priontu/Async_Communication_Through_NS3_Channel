from Network.Data_Management.Data_Packet import Data_Packet
import pandas as pd
import os
from typing import List

class Data_Collection_Manager:
    def __init__(self, save_dir = "results") -> None:
        self.dps: List[Data_Packet] = list() # Data Packets
        self.save_dir = save_dir

        self.ids = list()
        self.send_times = list()
        self.receive_times = list()
        self.detected_delays = list()
        self.sent_packet_count = None
        self.received_packet_count_list = list()
        self.final_received_packet_count = None
        self.expected_count = list()
        self.packet_sizes = list()
        self.slow_blocks = list()

        self.missing_packet_ids = list()
        self.missing_packet_count = None
        self.max_delay = None
        self.min_delay = None
        self.avg_delay = None
    
    def add_dps(self, dp):
        self.dps.append(dp)
    
    def print_attributes(self):
        print("\nCollected Data:")
        # print("Missing Ids: ", self.missing_packet_ids)
        print("Missing Packet Count: ", self.missing_packet_count)
        print("Maximum Delay: ", self.max_delay)
        print("Minimum Delay: ", self.min_delay)
        print("Average Delay; ", self.avg_delay)

    def prepare_all_data(self):
        self.record_all_ids()
        self.record_all_delays()
        self.record_sent_packet_count()
        self.record_expected_packet_count()
        self.record_missing_packet_info()
        self.record_max_delay()
        self.record_min_delay()
        self.record_avg_delay()
            
    def record_all_ids(self):
        for dp in self.dps:
            self.ids.append(dp.Packet_ID)
        return self.ids
    
    def record_all_delays(self):
        for dp in self.dps:
            self.detected_delays.append(dp.Detected_Delay)
        return self.detected_delays
    
    def record_sent_packet_count(self):
        highest = 0
        for dp in self.dps:
            if dp.Sent_Packet_Count > highest:
                highest = dp.Sent_Packet_Count
        self.sent_packet_count = highest
        return self.sent_packet_count

    def record_expected_packet_count(self):
        highest = 0
        for dp in self.dps:
            if dp.Expected_Count > highest:
                highest = dp.Expected_Count
        self.expected_count = highest  
        return self.expected_count

    def record_missing_packet_info(self):
        expected_ids = list(range(self.expected_count))
        self.missing_packet_ids = list(set(expected_ids) - set(self.ids))
        self.missing_packet_count = len(self.missing_packet_ids)
        return self.missing_packet_ids
    
    def record_max_delay(self):
         self.max_delay = max(self.detected_delays)
         return self.max_delay
    
    def record_min_delay(self):
        self.min_delay = min(self.detected_delays)
        return self.min_delay
    
    def record_avg_delay(self):
        # self.avg_delay = sum(self.detected_delays)/len(self.detected_delays)
        df = pd.Series(data=self.detected_delays)
        self.avg_delay = df.mean()
        return self.avg_delay
    
    def check_dir(self):
        is_exist = os.path.exists(self.save_dir)
        if not is_exist:
            print("Directory does not exist -- Creating directory.")
            os.makedirs(self.save_dir)

    def get_dp_collection_dict(self):
        dp_dict_list = list()

        for dp in self.dps:
            holder = dict()
            holder["Packet_ID"] = dp.Packet_ID
            holder["Send_Time"] = dp.Send_Time
            holder["Receive_Time"] = dp.Receive_Time
            holder["Detected_Delay"] = dp.Detected_Delay
            holder["Sent_Packet_Count"] = dp.Sent_Packet_Count
            holder["Received_Packet_Count"] = dp.Received_Packet_Count
            holder["Expected_Count"] = dp.Expected_Count
            holder["Packet_Size"] = dp.Packet_Size
            holder["Fast_Block_Size"] = dp.Fast_Block.Block_Size
            holder["Slow_Block_ID"] = dp.Slow_Block.Slow_Block_ID
            holder["Slow_Block_Size"] = dp.Slow_Block.Block_Size

            dp_dict_list.append(holder)
            
        return dp_dict_list

    # def save_data(self):




    
