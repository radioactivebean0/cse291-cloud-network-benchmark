sudo modprobe overlay
sudo modprobe br_netfilter

# automatically load kernel modules via the config file
cat <<EOF | sudo tee /etc/modules-load.d/kubernetes.conf
overlay
br_netfilter
EOF

lsmod | grep overlay
lsmod | grep br_netfilter
prompt ""

# setting up kernel parameters via config file
cat <<EOF | sudo tee /etc/sysctl.d/kubernetes.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF

# Applying new kernel parameters
sudo sysctl --system

sudo swapoff -a

# checking SWAP via /procs/swaps
cat /proc/swaps

# checking SWAP via command free -m
sudo free -m

# Creating environment variable $OS and $VERSION
export OS=xUbuntu_20.04
export VERSION=1.25

# Adding CRI-O repository for Ubuntu systems
echo "deb [signed-by=/usr/share/keyrings/libcontainers-archive-keyring.gpg] https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/$OS/ /" > /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list
echo "deb [signed-by=/usr/share/keyrings/libcontainers-crio-archive-keyring.gpg] https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable:/cri-o:/$VERSION/$OS/ /" > /etc/apt/sources.list.d/devel:kubic:libcontainers:stable:cri-o:$VERSION.list

# Creating directory /usr/share/keyrings
mkdir -p /usr/share/keyrings

# Downloading GPG key for CRI-O repository
curl -L https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/$OS/Release.key | gpg --dearmor -o /usr/share/keyrings/libcontainers-archive-keyring.gpg
curl -L https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable:/cri-o:/$VERSION/$OS/Release.key | gpg --dearmor -o /usr/share/keyrings/libcontainers-crio-archive-keyring.gpg

# Update and refresh package index
sudo apt update

# Install CRI-O container runtime
sudo apt install cri-o cri-o-runc

echo "Uncomment the lines 'network.dir' and 'plugin_dirs' right below it. They are under '[crio.network]'"
echo "Press enter when ready. This will open the file as sudo"
read
aws-west-t2-1vcpu-1gb

echo "Change ranges subnet from [{ "subnet": "10.85.0.0/16" }], to 10.42.5.0/24"
echo "Press enter when ready. This will open the file as sudo"
read 
vim /etc/cni/net.d/100-crio-bridge.conf

sudo systemctl restart crio

### Kubernetes installation
sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list

sudo apt update
sudo apt install kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl
#sudo kubeadm config images pull



# --apiserver-advertise-address=172.16.1.10
#sudo kubeadm init --pod-network-cidr=10.42.5.0/24 
#sudo kubeadm init --pod-network-cidr=10.42.5.0/24 --control-plane-endpoint=20.127.41.196