import time
import datetime
from Network.Data_Management.Data_Packet import Data_Packet
from Network.Data_Management.Data_Packet_Manager import DPM

from typing import List

class Buffer:
    def __init__(self) -> None:
        self.buffer: List[Data_Packet] = list()
        self.dropped_dps: List[Data_Packet] = list()

    
    def push(self, dp: Data_Packet):
        dp.Buffer_Push_Time = datetime.datetime.now()
        self.buffer.append(dp)
    
    def pop(self):
        dp = self.buffer.pop(0)
        dp.Buffer_Pop_Time = datetime.datetime.now()
        dp.Buffer_Time_Difference = dp.Buffer_Pop_Time - dp.Buffer_Push_Time
    
    def is_empty(self):
        if len(self.buffer) != 0:
            return False
        return True

    def drop_cycle(self, drop_time = datetime.timedelta(seconds=10)):
        time.sleep(8)
        while True:
            for i in range(len(self.buffer)):
                time_diff = datetime.datetime.now() - self.buffer[i].Buffer_Push_Time
                if time_diff >= drop_time:
                    self.dropped_dps.append(self.buffer.pop(i))
            time.sleep(1)
                    

    
