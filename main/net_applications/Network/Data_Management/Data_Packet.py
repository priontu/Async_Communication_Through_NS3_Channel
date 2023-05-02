class Fast_Block:
    # Fast_Block_ID = None
    # Content = None # Speed, RPM etc.
    Block_Size = None

class Slow_Block:
    Slow_Block_ID = None
    # Content = None # Tire Pressure, Oil Temperature etc.
    Block_Size = None

class Data_Packet:
    Packet_ID = None
    Send_Time = None
    Receive_Time = None
    Detected_Delay = None
    Sent_Packet_Count = None
    Received_Packet_Count = None
    Expected_Count = None
    Packet_Size = None
    Buffer_Push_Time = None
    Buffer_Pop_Time = None
    Buffer_Time_Difference = None
    Fast_Block = Fast_Block()
    Slow_Block = Slow_Block()
    Content = None
    # Slow_Block_ID = None
    # Slow_Block_Size = None
    # Fast_Block_Size = None