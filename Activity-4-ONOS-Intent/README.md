# Activity 4: Intent-Based Networking using ONOS

## Objective
To create a bandwidth-constrained host-to-host intent using ONOS and demonstrate automatic path rerouting following a link failure.

## Topology
A diamond topology was created using Mininet.

- Hosts: H1 and H2
- Switches: S1, S2, S3 and S4
- Primary path: S1 -> S2 -> S4
- Alternate path: S1 -> S3 -> S4

## Implementation
1. Created the diamond topology.
2. Connected the switches to the ONOS controller.
3. Verified device, host and link discovery.
4. Created a host-to-host intent with a bandwidth constraint of 10.
5. Verified that the intent reached the INSTALLED state.
6. Simulated a failure on the S1-S2 link.
7. Verified that ONOS selected the alternate path.
8. Tested host connectivity after rerouting.

## Technologies
- Mininet
- Open vSwitch 3.7.1
- ONOS Controller 3.0.0-SNAPSHOT
- OpenFlow 1.3
- Intent Framework

## Results

Initial intent:
- Intent ID: 0xa
- State: INSTALLED
- Path: S1 -> S2 -> S4

After link failure:
- Failed link: S1-S2
- Alternate path: S1 -> S3 -> S4
- Intent remained INSTALLED.

Final connectivity test:
- 10 packets transmitted
- 10 packets received
- 0% packet loss
- Average RTT: 0.261 ms

## Source Files
- `diamond.py`
- `intent_commands.txt`

## Execution
Refer to `intent_commands.txt` for the topology startup, intent creation, verification and link failure commands.
