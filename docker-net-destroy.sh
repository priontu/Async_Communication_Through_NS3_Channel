echo "Copy Datasets..."
counter=$(cat datasets/counter.txt)
counter=$((counter+1))
echo "Counter: ${counter}"

base_dir="datasets/dataset_${counter}/"
echo $base_dir
mkdir "$base_dir"
left_dir="$base_dir"/left
mkdir "$left_dir"
right_dir="$base_dir"/right
mkdir "$right_dir"
cp -r left_volume "$left_dir"
cp -r right_volume "$right_dir"

echo $counter > datasets/counter.txt


echo "Burning Bridges..."

ip link set br-left down
ip link set br-right down
sudo brctl delif br-left tap-left
sudo brctl delif br-right tap-right
brctl delbr br-left
brctl delbr br-right

sudo ifconfig tap-left down
sudo ifconfig tap-right down
sudo tunctl -d tap-left
sudo tunctl -d tap-right

ip link delete tap-left
ip link delete tap-right

ip link delete internal-left
ip link right internal-right

echo "Destroying Containers..."
docker container stop $(docker container ls -aq)
docker container rm $(docker container ls -aq)

docker container ls -a

echo "Deleting Docker Volumes..."
docker volume rm $(docker volume ls -q)
docker volume ls

rm -r left_volume
rm -r right_volume