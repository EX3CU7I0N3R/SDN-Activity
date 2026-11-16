# Activity 1: SDN Network Policy Enforcement

This monitor polls ONOS port counters and installs a permanent flow rule that drops ICMP packets matching a configured IPv4 source and destination when a port's measured rate exceeds a threshold.

## Requirements

- Python 3
- ONOS REST API enabled and reachable
- An OpenFlow switch connected to ONOS

Install the Python dependency:

```bash
python3 -m pip install -r requirements.txt
```

## Configure and run

```bash
export ONOS_URL=http://localhost:8181/onos/v1
export ONOS_USERNAME=onos
export ONOS_PASSWORD=rocks
export SOURCE_IP=10.0.0.1/32
export DESTINATION_IP=10.0.0.2/32
export THRESHOLD_MBPS=0.001
export POLL_INTERVAL=10
python3 network_policy.py
```

`ONOS_URL` is the ONOS API root. The script defaults to `http://localhost:8181/onos/v1`, username `onos`, source `10.0.0.1/32`, destination `10.0.0.2/32`, threshold `0.001` Mbps, and a 10-second poll interval. Keep the password in the environment rather than source control.

The first counter sample establishes a baseline. Later samples calculate each port's receive-plus-transmit byte rate independently. A switch receives the ICMP rule once after any port exceeds the threshold. The rule is permanent; remove it through ONOS when the lab is finished.
