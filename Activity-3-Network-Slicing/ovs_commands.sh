#!/bin/bash

# Activity 3: Network Slicing using VLANs and QoS
# Environment: Mininet, Open vSwitch, OpenFlow 1.3

set -e

SWITCH=${SWITCH:-s1}
UPLINK_PORT=${UPLINK_PORT:-1}
DOWNLINK_PORT=${DOWNLINK_PORT:-2}

if ! command -v ovs-vsctl >/dev/null || ! command -v ovs-ofctl >/dev/null; then
  echo "Open vSwitch commands are required." >&2
  exit 1
fi

if ! sudo ovs-vsctl br-exists "$SWITCH"; then
  echo "Open vSwitch bridge '$SWITCH' does not exist." >&2
  exit 1
fi

echo "Configuring VLAN trunk ports on $SWITCH..."

sudo ovs-vsctl set Port "$SWITCH-eth$UPLINK_PORT" vlan_mode=trunk trunks=100,200
sudo ovs-vsctl set Port "$SWITCH-eth$DOWNLINK_PORT" vlan_mode=trunk trunks=100,200

configure_qos() {
  local port=$1
  echo "Configuring QoS on $port..."

  sudo ovs-vsctl -- set Port "$port" qos=@qos \
  -- --id=@qos create QoS type=linux-htb \
  other-config:max-rate=100000000 \
  queues:1=@streaming queues:2=@control \
  -- --id=@streaming create Queue \
  other-config:min-rate=50000000 \
  other-config:max-rate=70000000 \
  -- --id=@control create Queue \
  other-config:min-rate=5000000 \
  other-config:max-rate=10000000
}

configure_qos "$SWITCH-eth$UPLINK_PORT"
configure_qos "$SWITCH-eth$DOWNLINK_PORT"

echo "Replacing this activity's OpenFlow rules..."
sudo ovs-ofctl -O OpenFlow13 del-flows "$SWITCH" "cookie=0x5103/0xffffffff"

sudo ovs-ofctl -O OpenFlow13 add-flow "$SWITCH" \
"cookie=0x5103,priority=50000,in_port=$UPLINK_PORT,dl_vlan=100,actions=set_queue:1,output:$DOWNLINK_PORT"

sudo ovs-ofctl -O OpenFlow13 add-flow "$SWITCH" \
"cookie=0x5103,priority=50000,in_port=$DOWNLINK_PORT,dl_vlan=100,actions=set_queue:1,output:$UPLINK_PORT"

sudo ovs-ofctl -O OpenFlow13 add-flow "$SWITCH" \
"cookie=0x5103,priority=50000,in_port=$UPLINK_PORT,dl_vlan=200,actions=set_queue:2,output:$DOWNLINK_PORT"

sudo ovs-ofctl -O OpenFlow13 add-flow "$SWITCH" \
"cookie=0x5103,priority=50000,in_port=$DOWNLINK_PORT,dl_vlan=200,actions=set_queue:2,output:$UPLINK_PORT"

echo "Configuration completed."
echo "Verify using ovs-vsctl list QoS, ovs-vsctl list Queue,"
echo "and ovs-ofctl -O OpenFlow13 dump-flows $SWITCH"
