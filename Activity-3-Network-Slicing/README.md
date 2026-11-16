# Activity 3: VLAN Network Slicing with QoS

This activity separates traffic into VLAN 100 and VLAN 200 and assigns the slices to separate Open vSwitch HTB queues.

| Slice | VLAN | Queue | Minimum rate | Maximum rate |
| --- | ---: | ---: | ---: | ---: |
| Streaming | 100 | 1 | 50 Mbps | 70 Mbps |
| Control | 200 | 2 | 5 Mbps | 10 Mbps |

The parent QoS rate is 100 Mbps. `ovs_commands.sh` configures two trunk ports on one Mininet switch, installs queue-selection flows in both directions, and replaces only the flows marked with this activity's cookie when rerun.

## Requirements

- Linux with Mininet and Open vSwitch installed
- A running bridge (default `s1`) with the two ports used by the traffic path
- `sudo` access

## Run

```bash
sudo ./ovs_commands.sh
```

Set `SWITCH`, `UPLINK_PORT`, and `DOWNLINK_PORT` to match your topology. For example:

```bash
sudo env SWITCH=s2 UPLINK_PORT=3 DOWNLINK_PORT=4 ./ovs_commands.sh
```

The script configures switch ports and flows; configure VLAN interfaces on hosts separately so their traffic is tagged with VLAN 100 or 200. Verify with:

```bash
sudo ovs-vsctl list QoS
sudo ovs-vsctl list Queue
sudo ovs-ofctl -O OpenFlow13 dump-flows s1
```

The original lab observed successful ping connectivity and queue counters. Those results show reachability and queue use; they do not establish latency guarantees or prove a performance advantage for either slice.
