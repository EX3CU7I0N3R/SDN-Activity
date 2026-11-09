import requests
import time
import os


# ONOS Controller Configuration
ONOS_URL = os.getenv("ONOS_URL", "http://localhost:8181/onos/v1")
USERNAME = os.getenv("ONOS_USERNAME", "onos")
PASSWORD = os.getenv("ONOS_PASSWORD")

if not PASSWORD:
    raise ValueError("Please set the ONOS_PASSWORD environment variable.")

# Network Configuration
DEVICE_ID = "of:0000000000000001"
SOURCE_IP = "10.0.0.1/32"
DESTINATION_IP = "10.0.0.2/32"

THRESHOLD_MBPS = 0.001
POLL_INTERVAL = 10

# Create HTTP session
session = requests.Session()
session.auth = (USERNAME, PASSWORD)


# Function 1: Fetch connected switches
def get_switches():
    response = session.get(f"{ONOS_URL}/devices")
    response.raise_for_status()

    devices = response.json()["devices"]

    connected_switches = [
        device["id"]
        for device in devices
        if device.get("available") is True
    ]

    return connected_switches


# Function 2: Fetch port statistics
def get_port_statistics(device_id):
    url = f"{ONOS_URL}/statistics/ports/{device_id}"

    response = session.get(url)
    response.raise_for_status()

    data = response.json()

    return data.get("statistics", [])


# Function 3: Calculate bandwidth
def calculate_bandwidth(current_bytes, previous_bytes, elapsed_time):
    if previous_bytes is None or elapsed_time <= 0:
        return 0

    bytes_transferred = max(0, current_bytes - previous_bytes)

    bandwidth_bps = (bytes_transferred * 8) / elapsed_time

    return bandwidth_bps / 1_000_000


# Function 4: Block ICMP traffic
def block_icmp(device_id):
    url = f"{ONOS_URL}/flows/{device_id}"

    flow_rule = {
        "priority": 40000,
        "timeout": 0,
        "isPermanent": True,
        "deviceId": device_id,
        "treatment": {
            "instructions": []
        },
        "selector": {
            "criteria": [
                {
                    "type": "ETH_TYPE",
                    "ethType": "0x0800"
                },
                {
                    "type": "IP_PROTO",
                    "protocol": 1
                },
                {
                    "type": "IPV4_SRC",
                    "ip": SOURCE_IP
                },
                {
                    "type": "IPV4_DST",
                    "ip": DESTINATION_IP
                }
            ]
        }
    }

    response = session.post(url, json=flow_rule)
    response.raise_for_status()

    print("ICMP blocking flow rule submitted successfully!")


# Main monitoring function
def main():

    print("Starting SDN Network Policy Engine...")

    previous_counters = {}
    previous_time = time.time()
    blocked_switches = set()

    while True:

        try:
            switches = get_switches()

            if not switches:
                print("No connected switches found.")
                time.sleep(POLL_INTERVAL)
                continue

            for device_id in switches:

                print("\nConnected Switch:", device_id)

                statistics = get_port_statistics(device_id)

                current_time = time.time()
                elapsed_time = current_time - previous_time

                for stat in statistics:

                    for port in stat.get("ports", []):

                        port_id = port["port"]
                        current_bytes = (
                            port["bytesReceived"] + port["bytesSent"]
                        )

                        key = (device_id, port_id)

                        previous_bytes = previous_counters.get(key)

                        bandwidth = calculate_bandwidth(
                            current_bytes,
                            previous_bytes,
                            elapsed_time
                        )

                        previous_counters[key] = current_bytes

                        print(
                            f"Port {port_id}: "
                            f"{bandwidth:.4f} Mbps"
                        )

                        if bandwidth > THRESHOLD_MBPS:
                            print("Traffic threshold exceeded!")

                            if device_id not in blocked_switches:
                                block_icmp(device_id)
                                blocked_switches.add(device_id)

            previous_time = time.time()
            time.sleep(POLL_INTERVAL)

        except requests.exceptions.RequestException as error:
            print("Controller communication error:", error)
            time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            print("\nNetwork Policy Engine stopped.")
            break


if __name__ == "__main__":
    main()
