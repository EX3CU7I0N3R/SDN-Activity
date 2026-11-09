# Activity 1: SDN-Based Network Policy Enforcement

## Objective
To implement a network policy engine using the ONOS SDN controller that monitors network traffic and applies flow rules when a configured bandwidth threshold is exceeded.

## Implementation
- Connects to the ONOS REST API.
- Retrieves available switches and port statistics.
- Calculates bandwidth using differences in transmitted and received byte counters.
- Compares measured bandwidth against a configured threshold.
- Installs a flow rule to block matching ICMP traffic when the threshold is exceeded.

## Technologies
- Python
- ONOS Controller
- REST API
- OpenFlow
- Requests library

## Configuration
Set the ONOS credentials using environment variables:

```bash


export ONOS_URL=http://localhost:8181/onos/v1
export ONOS_USERNAME=onos
export ONOS_PASSWORD='your-ONOS-password'
