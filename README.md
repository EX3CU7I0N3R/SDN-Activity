# Software Defined Networking Class Activities

Four hands-on SDN activities using ONOS, Mininet, Open vSwitch, OpenFlow, and Python/Java. Each activity has its own source files and run notes.

## Activities

| Activity | Topic | Main files |
| --- | --- | --- |
| [1. Network policy](Activity-1-Network-Policy/) | Monitor switch port traffic through ONOS and install a matching ICMP flow when the configured rate is exceeded. | `network_policy.py` |
| [2. Broadcast guard](Activity-2-Broadcast-Guard/) | ONOS packet processor with source MAC learning and duplicate broadcast suppression. | `pom.xml`, `src/main/java/` |
| [3. Network slicing](Activity-3-Network-Slicing/) | VLAN 100/200 traffic queues with Open vSwitch HTB QoS. | `ovs_commands.sh` |
| [4. ONOS intent](Activity-4-ONOS-Intent/) | Host-to-host bandwidth intent over a Mininet diamond topology with link-failure rerouting. | `diamond.py`, `intent_commands.txt` |

## Prerequisites

- Linux host or VM with Mininet and Open vSwitch for topology and QoS activities.
- ONOS controller reachable from the Mininet switches; the activities use its REST API and/or intent CLI.
- Python 3 and `pip` for Activity 1; Java 17 and Maven for Activity 2.
- OpenFlow 1.3 enabled on the Mininet switches.

ONOS versions and command syntax can vary by installation. Use the ONOS API and CLI version matching the controller you run.

## Quick start

### Activity 1: Network policy monitor

```bash
cd Activity-1-Network-Policy
python3 -m pip install -r requirements.txt
export ONOS_URL=http://localhost:8181/onos/v1
export ONOS_USERNAME=onos
export ONOS_PASSWORD=rocks
python3 network_policy.py
```

Set `THRESHOLD_MBPS`, `POLL_INTERVAL`, `SOURCE_IP`, and `DESTINATION_IP` in the environment to override the defaults. The monitor uses each port's counter delta between polls. When a port exceeds the configured threshold, it installs a permanent ICMP drop rule for the configured source and destination on that switch. Review the threshold and flow selector for your lab before running it.

### Activity 2: Broadcast guard

```bash
cd Activity-2-Broadcast-Guard
mvn clean package
```

Install the resulting bundle on the matching ONOS controller using the deployment command for that ONOS version. See the [activity notes](Activity-2-Broadcast-Guard/README.md) for behavior and limitations.

### Activity 3: Network slicing

Run from a Linux shell where the Mininet bridge already exists and has two ports numbered 1 and 2:

```bash
cd Activity-3-Network-Slicing
sudo ./ovs_commands.sh
```

Override `SWITCH`, `UPLINK_PORT`, or `DOWNLINK_PORT` when your bridge or port numbers differ. The script configures VLAN trunks, HTB queues, and the queue-selection flows. Configure the host VLAN interfaces separately as described in the [activity notes](Activity-3-Network-Slicing/README.md).

### Activity 4: Intent rerouting

Copy `diamond.py` to the Linux Mininet host, then start Mininet with the custom topology:

```bash
sudo mn --custom diamond.py --topo diamond \
  --controller remote,ip=127.0.0.1,port=6653 \
  --switch ovsk,protocols=OpenFlow13
```

Use the commands in [`intent_commands.txt`](Activity-4-ONOS-Intent/intent_commands.txt) from the ONOS CLI and Mininet CLI to install the intent, inspect the selected path, disable a link, and confirm rerouting.

## Repository layout

```text
SDNassmain/
├── Activity-1-Network-Policy/
│   ├── network_policy.py
│   ├── requirements.txt
│   └── README.md
├── Activity-2-Broadcast-Guard/
│   ├── pom.xml
│   ├── src/main/java/org/onosproject/broadcastguard/
│   └── README.md
├── Activity-3-Network-Slicing/
│   ├── ovs_commands.sh
│   └── README.md
├── Activity-4-ONOS-Intent/
│   ├── diamond.py
│   ├── intent_commands.txt
│   └── README.md
└── README.md
```

## License

No license is currently specified. Add one before redistributing or reusing this project outside your coursework.
