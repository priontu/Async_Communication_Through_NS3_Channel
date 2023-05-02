#!/bin/sh
docker build -t left main/
docker build -t right main/

mkdir left_volume
mkdir right_volume

docker volume create --name left_volume --opt type=None --opt device="$(pwd)"/left_volume --opt o=bind
docker volume create --name right_volume --opt type=None --opt device="$(pwd)"/right_volume --opt o=bind

# docker run --name left --network none --privileged -itd ramansingh1984/dweb-base:dweb-base-ubuntu
# docker run --name right --network none --privileged -itd ramansingh1984/dweb-base:dweb-base-ubuntu

docker run --mount source=left_volume,target=/home/net_applications/results --network none --privileged -itd --name left left
docker run --mount source=right_volume,target=/home/net_applications/results --network none --privileged -itd --name right right

pid_left=$(docker inspect --format '{{ .State.Pid }}' left)
pid_right=$(docker inspect --format '{{ .State.Pid }}' right)

sudo brctl addbr br-left
sudo brctl addbr br-right

sudo tunctl -t tap-left
sudo tunctl -t tap-right

sudo ifconfig tap-left 0.0.0.0 promisc up
sudo ifconfig tap-right 0.0.0.0 promisc up

sudo brctl addif br-left tap-left
sudo ifconfig br-left up
sudo brctl addif br-right tap-right
sudo ifconfig br-right up

pushd /proc/sys/net/bridge
for f in bridge-nf-*; do echo 0 > $f; done
popd

echo "PID Left:"
echo $pid_left
sudo mkdir -p /var/run/netns
sudo ln -s /proc/$pid_left/ns/net /var/run/netns/$pid_left

sudo ip link add internal-left type veth peer name external-left
sudo brctl addif br-left internal-left
sudo ip link set internal-left up

sudo ip link set external-left netns $pid_left

sudo ip netns exec $pid_left ip link set dev external-left name eth0
sudo ip netns exec $pid_left ip link set eth0 address 12:34:88:5D:61:BD
# sudo ip netns exec $pid_left ip addr add 10.0.0.1/16 dev eth0
sudo ip netns exec $pid_left ip addr add 10.1.1.3/24 brd + dev eth0
sudo ip netns exec $pid_left ip link set eth0 up
sudo ip netns exec $pid_left ip route add 10.1.2.0/24 via 10.1.1.2
sudo ip netns exec $pid_left ip route add 10.1.3.0/24 via 10.1.1.2

sudo ip netns exec $pid_left route -n

echo "PID Right:"
echo $pid_right
sudo ln -s /proc/$pid_right/ns/net /var/run/netns/$pid_right
sudo ip link add internal-right type veth peer name external-right
sudo brctl addif br-right internal-right
sudo ip link set internal-right up
sudo ip link set external-right netns $pid_right

sudo ip netns exec $pid_right ip link set dev external-right name eth0
sudo ip netns exec $pid_right ip link set eth0 address 5A:34:88:5D:61:BD
sudo ip netns exec $pid_right ip link set eth0 up
# sudo ip netns exec $pid_right ip addr add 10.0.0.2/16 dev eth0
sudo ip netns exec $pid_right ip addr add 10.1.3.3/24 brd + dev eth0
sudo ip netns exec $pid_right ip route add 10.1.1.0/24 via 10.1.3.2
sudo ip netns exec $pid_right ip route add 10.1.2.0/24 via 10.1.3.2

sudo ip netns exec $pid_right route -n

# sudo docker cp udp_client_server/client.py left:/home/
# sudo docker cp setup_sources.sh left:/home/
# sudo docker cp udp_client_server/server.py right:/home/
# sudo docker cp setup_sources.sh right:/home/

# sudo docker exec left /bin/bash -c "python3 home/net_applications/async_udp_server.py --host=\"10.1.1.3\" --port=5050"
# sudo docker exec right /bin/bash -c "python3 home/net_applications/async_udp_client.py --host=\"10.1.1.3\" --port=5050"
# sudo docker exec right /bin/bash -c "chmod +x home/setup_sources.sh"

# sudo docker exec left /home/setup_sources.sh
# sudo docker exec right /home/setup_sources.sh