/*
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

//
// This is an illustration of how one could use virtualization techniques to
// allow running applications on virtual machines talking over simulated
// networks.
//
// The actual steps required to configure the virtual machines can be rather
// involved, so we don't go into that here.  Please have a look at one of
// our HOWTOs on the nsnam wiki for more details about how to get the
// system confgured.  For an example, have a look at "HOWTO Use Linux
// Containers to set up virtual networks" which uses this code as an
// example.
//
// The configuration you are after is explained in great detail in the
// HOWTO, but looks like the following:
//
//  +----------+                           +----------+
//  | virtual  |                           | virtual  |
//  |  Linux   |                           |  Linux   |
//  |   Host   |                           |   Host   |
//  |          |                           |          |
//  |   eth0   |                           |   eth0   |
//  +----------+                           +----------+
//       |                                      |
//  +----------+                           +----------+
//  |  Linux   |                           |  Linux   |
//  |  Bridge  |                           |  Bridge  |
//  +----------+                           +----------+
//       |                                      |
//  +------------+                       +-------------+
//  | "tap-left" |                       | "tap-right" |
//  +------------+                       +-------------+
//       |           n0            n1           |
//       |       +--------+    +--------+       |
//       +-------|  tap   |    |  tap   |-------+
//               | bridge |    | bridge |
//               +--------+    +--------+
//               |  CSMA  |    |  CSMA  |
//               +--------+    +--------+
//                   |             |
//                   |             |
//                   |             |
//                   ===============
//                      CSMA LAN
//
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

#include <fstream>
#include <iostream>
#include <string>

using namespace ns3;

NS_LOG_COMPONENT_DEFINE("TapCsmaVirtualMachineExample");

void ChangeParams(){
    Config::Set("/ChannelList/0/$ns3::CsmaChannel/Delay", TimeValue(Seconds(2)));
    Config::Set("/ChannelList/0/$ns3::CsmaChannel/DataRate", StringValue("10Mbps"));
}

int
main(int argc, char* argv[])
{
    CommandLine cmd(__FILE__);
    cmd.Parse(argc, argv);

    //
    // We are interacting with the outside, real, world.  This means we have to
    // interact in real-time and therefore means we have to use the real-time
    // simulator and take the time to calculate checksums.
    //
    GlobalValue::Bind("SimulatorImplementationType", StringValue("ns3::RealtimeSimulatorImpl"));
    GlobalValue::Bind("ChecksumEnabled", BooleanValue(true));

    //
    // Create two ghost nodes.  The first will represent the virtual machine host
    // on the left side of the network; and the second will represent the VM on
    // the right side.
    //
    
    // NodeContainer p2p_nodes;
    // p2p_nodes.Create(2);
    
    NodeContainer csma_nodes_left;
    csma_nodes_left.Create(2);
    // csma_nodes_left.Add(p2p_nodes.Get(0));

    NodeContainer csma_nodes_right;
    // csma_nodes_right.Add(p2p_nodes.Get(1));
    csma_nodes_right.Create(2);

    NodeContainer p2p_nodes = NodeContainer(csma_nodes_left.Get(1), csma_nodes_right.Get(0));



    //
    // Use a CsmaHelper to get a CSMA channel created, and the needed net
    // devices installed on both of the nodes.  The data rate and delay for the
    // channel can be set through the command-line parser.  For example,
    //
    // ./ns3 run "tap-csma-virtual-machine --ns3::CsmaChannel::DataRate=10000000"
    //
    CsmaHelper csma;

    csma.SetChannelAttribute("DataRate", StringValue("1Mbps"));
    csma.SetChannelAttribute("Delay", TimeValue(MilliSeconds(10)));
    NetDeviceContainer csma_devices_left = csma.Install(csma_nodes_left);
    NetDeviceContainer csma_devices_right = csma.Install(csma_nodes_right);

    PointToPointHelper pointToPoint;
    pointToPoint.SetDeviceAttribute ("DataRate", StringValue ("5Mbps"));
    pointToPoint.SetChannelAttribute ("Delay", StringValue ("2ms"));

    NetDeviceContainer p2p_devices;
    p2p_devices = pointToPoint.Install (p2p_nodes);
//    Config::Set("/NodeList/0/ChannelList/0/$ns3::CsmaNetDevice/DataRate", StringValue("1Mbps"));
//    Config::SetDefault("/NodeList/0/ChannelList/0/$ns3::CsmaNetDevice/DataRate", TimeValue(Seconds(100)));
    //
    // Use the TapBridgeHelper to connect to the pre-configured tap devices for
    // the left side.  We go with "UseBridge" mode since the CSMA devices support
    // promiscuous mode and can therefore make it appear that the bridge is
    // extended into ns-3.  The install method essentially bridges the specified
    // tap to the specified CSMA device.
    //
    InternetStackHelper stack;
    stack.Install(csma_nodes_left);
    stack.Install(csma_nodes_right);

    Ipv4AddressHelper address;
    address.SetBase("10.1.1.0", "255.255.255.0");
    Ipv4InterfaceContainer p2p_interfaces;
    p2p_interfaces = address.Assign(p2p_devices);

    address.SetBase("10.1.2.0", "255.255.255.0");
    Ipv4InterfaceContainer csma_interfaces_left;
    csma_interfaces_left = address.Assign(csma_devices_left);

    address.SetBase("10.1.3.0", "255.255.255.0");
    Ipv4InterfaceContainer csma_interfaces_right;
    csma_interfaces_right = address.Assign(csma_devices_right);

    Ipv4GlobalRoutingHelper::PopulateRoutingTables();


    TapBridgeHelper tapBridge;
    tapBridge.SetAttribute("Mode", StringValue("UseBridge"));
    tapBridge.SetAttribute("DeviceName", StringValue("tap-left"));
    tapBridge.Install(csma_nodes_left.Get(0), csma_devices_left.Get(0));

    //
    // Connect the right side tap to the right side CSMA device on the right-side
    // ghost node.
    //
    tapBridge.SetAttribute("DeviceName", StringValue("tap-right"));
    tapBridge.Install(csma_nodes_right.Get(1), csma_devices_right.Get(1));

    //std::cout << "DataRate: " << csma.GetDataRate();

    // Simulator::Schedule(Seconds(10),  &ChangeParams);

    // Simulator::Schedule(Seconds(20.0), Config::Set, "/ChannelList/0/$ns3::CsmaChannel/Delay", TimeValue(Seconds(1)));
    // Simulator::Schedule(Seconds(20.0), Config::Set, "/ChannelList/0/$ns3::CsmaChannel/DataRate", StringValue("0.1Mbps"));
    //
    // Run the simulation for ten minutes to give the user time to play around
    //

    // Changing Data Rate and Delay:
    // float time_val;
    // float datarate = 10; //Mbps
    // std::string datarate_str;
    // std::cout << "Scheduled Attributes: " << std::endl;
    // for (int i = 0; i <= 1800; i++){
    //     time_val = static_cast<float>(i);
    //     if (datarate > 0.01){
    //         datarate = datarate - 0.01;
    //         datarate_str = std::to_string(datarate);
    //         datarate_str = datarate_str + "Mbps";
    //         std::cout << "Second: " << time_val << " DataRate Str: " << datarate_str << std::endl;
    //         Simulator::Schedule(Seconds(time_val), Config::Set, "/ChannelList/0/$ns3::CsmaChannel/DataRate", StringValue(datarate_str));
    //     }
    // }
    csma.EnablePcap("left-tap-node", csma_devices_left.Get(0), true);
    csma.EnablePcap("right-tap-node", csma_devices_right.Get(1), true);
    csma.EnablePcap("left-p2p-node", csma_devices_left.Get(0), true);
    csma.EnablePcap("right-p2p-node", csma_devices_right.Get(1), true);
    pointToPoint.EnablePcapAll("p2p");

    // AnimationInterface anim("csma_p2p.xml");

    Simulator::Stop(Seconds(1800.));
    Simulator::Run();
    Simulator::Destroy();
}
