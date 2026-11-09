#!/bin/bash

# Activity 3: Network Slicing using VLANs and QoS
# Environment: Mininet, Open vSwitch, OpenFlow 1.3

set -e

echo "Configuring VLAN trunk ports..."

sudo ovs-vsctl set Port s1-eth1 vlan_mode=trunk trunks=100,200
sudo ovs-vsctl set Port s1-eth2 vlan_mode=trunk trunks=100,200

echo "Configuring QoS on port s1-eth1..."

sudo ovs-vsctl -- set Port s1-eth1 qos=@qos1 \
  -- --id=@qos1 create QoS type=linux-htb \
  other-config:max-rate=100000000 \
  queues:1=@q1 queues:2=@q2 \
  -- --id=@q1 create Queue \
  other-config:min-rate=50000000 \
  other-config:max-rate=70000000 \
  -- --id=@q2 create Queue \
  other-config:min-rate=5000000 \
  other-config:max-rate=10000000

echo "Configuring QoS on port s1-eth2..."

sudo ovs-vsctl -- set Port s1-eth2 qos=@qos1 \
  -- --id=@qos1 create QoS type=linux-htb \
  other-config:max-rate=100000000 \
  queues:1=@q1 queues:2=@q2 \
  -- --id=@q1 create Queue \
  other-config:min-rate=50000000 \
  other-config:max-rate=70000000 \
  -- --id=@q2 create Queue \
  other-config:min-rate=5000000 \
  other-config:max-rate=10000000

echo "Installing OpenFlow queue assignment rules..."

sudo ovs-ofctl -O OpenFlow13 add-flow s1 \
"priority=50000,in_port=1,dl_vlan=100,actions=set_queue:1,output:2"

sudo ovs-ofctl -O OpenFlow13 add-flow s1 \
"priority=50000,in_port=2,dl_vlan=100,actions=set_queue:1,output:1"

sudo ovs-ofctl -O OpenFlow13 add-flow s1 \
"priority=50000,in_port=1,dl_vlan=200,actions=set_queue:2,output:2"

sudo ovs-ofctl -O OpenFlow13 add-flow s1 \
"priority=50000,in_port=2,dl_vlan=200,actions=set_queue:2,output:1"

echo "Configuration completed."
echo "Verify using ovs-vsctl list QoS, ovs-vsctl list Queue,"
echo "and ovs-ofctl -O OpenFlow13 dump-flows s1"
