#include <iostream>

#include <fstream>

 
#include "ns3/core-module.h"
#include "ns3/csma-module.h"
#include "ns3/network-module.h"
#include "ns3/tap-bridge-module.h"
#include "ns3/core-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"
#include "ns3/ipv4-global-routing-helper.h"

#include "ns3/netanim-module.h"
#include "ns3/internet-module.h"
#include "ns3/error-model.h"
#include "ns3/config-store-module.h"
#include "ns3/flow-monitor-helper.h"

 

using namespace ns3;

 

NS_LOG_COMPONENT_DEFINE ("TapCsmaUseBridgeExample");

void change_params(){
	Config::Set("/NodeList/2/DeviceList/2/$ns3::PointToPointNetDevice/DataRate", StringValue("0.1Mbps") );
}
 

int

main (int argc, char *argv[])
{
	CommandLine cmd (__FILE__);
	cmd.Parse (argc, argv);



	//

	// We are interacting with the outside, real, world.  This means we have to
	// interact in real-time and therefore means we have to use the real-time
	// simulator and take the time to calculate checksums.
	//

	GlobalValue::Bind ("SimulatorImplementationType", StringValue ("ns3::RealtimeSimulatorImpl"));
	GlobalValue::Bind ("ChecksumEnabled", BooleanValue (true));
	//
	// Create two ghost nodes.  The first will represent the virtual machine host
	// on the left side of the network; and the second will represent the VM on
	// the right side.
	//

	NodeContainer csma1Nodes;
	csma1Nodes.Create (2);

	NodeContainer p2pNodes;
	p2pNodes.Add (csma1Nodes.Get (1));
	p2pNodes.Create(1);



	NodeContainer csma2Nodes;
	csma2Nodes.Create(1);
	csma2Nodes.Add (p2pNodes.Get (1));



	PointToPointHelper pointToPoint;
	pointToPoint.SetDeviceAttribute ("DataRate", StringValue ("200Kbps"));
	pointToPoint.SetChannelAttribute ("Delay", StringValue ("2ms"));



	NetDeviceContainer p2pDevices;
	p2pDevices = pointToPoint.Install (p2pNodes);



	CsmaHelper csma;
	csma.SetChannelAttribute ("DataRate", StringValue ("100Mbps"));
	csma.SetChannelAttribute ("Delay", TimeValue (NanoSeconds (10)));



	NetDeviceContainer csma1Devices;
	NetDeviceContainer csma2Devices;
	csma1Devices = csma.Install (csma1Nodes);
	csma2Devices = csma.Install (csma2Nodes);



	Ptr<RateErrorModel> em = CreateObject<RateErrorModel> ();
	em->SetAttribute ("ErrorRate", DoubleValue (0.01));
	em->SetAttribute ("ErrorUnit", StringValue ("ERROR_UNIT_PACKET"));
	p2pDevices.Get (1)->SetAttribute ("ReceiveErrorModel", PointerValue (em));



	InternetStackHelper stack;
	stack.Install (csma1Nodes);
	stack.Install (csma2Nodes);



	Ipv4AddressHelper address;
	address.SetBase ("10.1.1.0", "255.255.255.0");
	Ipv4InterfaceContainer csma1Interfaces;
	csma1Interfaces = address.Assign (csma1Devices);



	address.SetBase ("10.1.2.0", "255.255.255.0");
	Ipv4InterfaceContainer p2pInterfaces;
	p2pInterfaces = address.Assign (p2pDevices);



	address.SetBase ("10.1.3.0", "255.255.255.0");
	Ipv4InterfaceContainer csma2Interfaces;
	csma2Interfaces = address.Assign (csma2Devices);


	Ipv4GlobalRoutingHelper::PopulateRoutingTables ();



	//TapBridgeHelper tapBridge;
	//tapBridge.SetAttribute ("Mode", StringValue ("ConfigureLocal"));
	//tapBridge.SetAttribute ("DeviceName", StringValue ("thetap"));
	//tapBridge.Install (csma1Nodes.Get (0), csma1Devices.Get (0));



	//
	// Use the TapBridgeHelper to connect to the pre-configured tap devices for
	// the left side.  We go with "UseBridge" mode since the CSMA devices support
	// promiscuous mode and can therefore make it appear that the bridge is
	// extended into ns-3.  The install method essentially bridges the specified
	// tap to the specified CSMA device.
	//

	TapBridgeHelper tapBridge;
	tapBridge.SetAttribute ("Mode", StringValue ("UseBridge"));
	tapBridge.SetAttribute ("DeviceName", StringValue ("tap-left"));
	tapBridge.Install (csma1Nodes.Get (0), csma1Devices.Get (0));



	//
	// Connect the right side tap to the right side CSMA device on the right-side
	// ghost node.
	//

	tapBridge.SetAttribute ("DeviceName", StringValue ("tap-right"));

	tapBridge.Install (csma2Nodes.Get (0), csma2Devices.Get (0));

	csma.EnablePcap("left-tap-node", csma1Devices.Get(0), true);
	csma.EnablePcap("right-tap-node", csma2Devices.Get(1), true);
	csma.EnablePcap("left-p2p-node", csma1Devices.Get(0), true);
	csma.EnablePcap("right-p2p-node", csma2Devices.Get(1), true);
	pointToPoint.EnablePcapAll("p2p"); 

	// Simulator::Schedule(Seconds(5.0), Config::Set, "NodeList/1/$ns3::Node/DeviceList/0/$ns3::PointToPointNetDevice/DataRate", StringValue("0.001Mbps"));
	// Simulator::Schedule(Seconds(5.0), Config::Set, "NodeList/2/$ns3::Node/DeviceList/0/$ns3::PointToPointNetDevice/DataRate", StringValue("0.001Mbps"));

    // Changing Data Rate and Delay:
    float time_val;
    float datarate = 200; //Kbps
    std::string datarate_str;
    std::cout << "Scheduled Attributes: " << std::endl;
    for (int i = 0; i <= 1800; i++){
        time_val = static_cast<float>(i);
        datarate = datarate - 1;
        if (datarate > 1){
            datarate_str = std::to_string(datarate);
            datarate_str = datarate_str + "Kbps";
            std::cout << "Second: " << time_val << " DataRate:  " << datarate_str << std::endl;
            // Simulator::Schedule(Seconds(time_val), Config::Set, "/ChannelList/0/$ns3::CsmaChannel/DataRate", StringValue(datarate_str));
			Simulator::Schedule(Seconds(i), Config::Set, "NodeList/1/$ns3::Node/DeviceList/0/$ns3::PointToPointNetDevice/DataRate", StringValue(datarate_str));
			Simulator::Schedule(Seconds(i), Config::Set, "NodeList/2/$ns3::Node/DeviceList/0/$ns3::PointToPointNetDevice/DataRate", StringValue(datarate_str));
        }
    }

	Ptr<FlowMonitor> flowMonitor;
	FlowMonitorHelper flowHelper;
	flowMonitor = flowHelper.InstallAll();

		//
		// Run the simulation for ten minutes to give the user time to play around
		//
	Config::SetDefault ("ns3::ConfigStore::Filename", StringValue ("output-attributes.txt"));
	Config::SetDefault ("ns3::ConfigStore::FileFormat", StringValue ("RawText"));
	Config::SetDefault ("ns3::ConfigStore::Mode", StringValue ("Save"));
	ConfigStore outputConfig2;
	outputConfig2.ConfigureDefaults ();
	outputConfig2.ConfigureAttributes ();

	Simulator::Stop (Seconds (200));
	Simulator::Run ();

	flowMonitor->SerializeToXmlFile("FlowMonitor.xml", true, true);

	Simulator::Destroy ();

}