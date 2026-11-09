# Activity 3: Network Slicing using VLAN and QoS

## Objective
To implement logical network slices using VLAN tagging and Quality of Service (QoS) queues in Open vSwitch.

## Network Design

Two logical slices were configured:

| Slice | VLAN ID | Queue | Minimum Rate | Maximum Rate |
|---|---:|---:|---:|---:|
| Streaming | 100 | 1 | 50 Mbps | 70 Mbps |
| Control | 200 | 2 | 5 Mbps | 10 Mbps |

The parent QoS rate was configured to 100 Mbps.

## Implementation
- Configured VLAN trunking on switch ports.
- Created Linux HTB QoS queues.
- Assigned VLAN 100 traffic to Queue 1.
- Assigned VLAN 200 traffic to Queue 2.
- Installed OpenFlow 1.3 rules to direct traffic to the corresponding queues.

## Technologies
- Mininet
- Open vSwitch 3.7.1
- ONOS Controller
- VLAN
- OpenFlow 1.3
- Linux HTB

## Verification Results

VLAN 100 connectivity:
- 10 packets transmitted
- 10 packets received
- 0% packet loss
- Average RTT: 1.159 ms

VLAN 200 connectivity:
- 10 packets transmitted
- 10 packets received
- 0% packet loss
- Average RTT: 0.379 ms

Queue statistics showed 12 packets in each queue and zero errors.

## Important Observation
The experiment verified VLAN connectivity and queue traffic counters. The ping results do not establish a latency guarantee or prove that one slice has lower latency than the other.

## Source Files
- `ovs_commands.sh`
- `README.md`

## Execution
Run the commands in `ovs_commands.sh` in the configured Mininet and Open vSwitch environment. Host VLAN interfaces must also be configured as described in the lab setup.
