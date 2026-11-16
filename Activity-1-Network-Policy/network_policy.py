import os
import time

import requests


ONOS_URL = os.getenv("ONOS_URL", "http://localhost:8181/onos/v1").rstrip("/")
ONOS_USERNAME = os.getenv("ONOS_USERNAME", "onos")
ONOS_PASSWORD = os.getenv("ONOS_PASSWORD")
SOURCE_IP = os.getenv("SOURCE_IP", "10.0.0.1/32")
DESTINATION_IP = os.getenv("DESTINATION_IP", "10.0.0.2/32")
THRESHOLD_MBPS = float(os.getenv("THRESHOLD_MBPS", "0.001"))
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", "10"))
REQUEST_TIMEOUT = 10


def create_session():
    if not ONOS_PASSWORD:
        raise RuntimeError("Set ONOS_PASSWORD before starting the policy monitor.")

    session = requests.Session()
    session.auth = (ONOS_USERNAME, ONOS_PASSWORD)
    return session


def get_switches(session):
    response = session.get(f"{ONOS_URL}/devices", timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return [
        device["id"]
        for device in response.json().get("devices", [])
        if device.get("available") is True
    ]


def get_port_statistics(session, device_id):
    response = session.get(
        f"{ONOS_URL}/statistics/ports/{device_id}", timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()
    return response.json().get("statistics", [])


def calculate_bandwidth(current_bytes, previous_sample):
    if previous_sample is None:
        return None

    previous_bytes, previous_time = previous_sample
    elapsed = time.monotonic() - previous_time
    if elapsed <= 0:
        return None

    transferred = max(0, current_bytes - previous_bytes)
    return transferred * 8 / elapsed / 1_000_000


def block_icmp(session, device_id):
    flow_rule = {
        "priority": 40000,
        "timeout": 0,
        "isPermanent": True,
        "deviceId": device_id,
        "treatment": {"instructions": []},
        "selector": {
            "criteria": [
                {"type": "ETH_TYPE", "ethType": "0x0800"},
                {"type": "IP_PROTO", "protocol": 1},
                {"type": "IPV4_SRC", "ip": SOURCE_IP},
                {"type": "IPV4_DST", "ip": DESTINATION_IP},
            ]
        },
    }
    response = session.post(
        f"{ONOS_URL}/flows/{device_id}", json=flow_rule, timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()


def monitor(session):
    previous_counters = {}
    blocked_switches = set()

    print("Starting SDN network policy monitor.")
    while True:
        try:
            switches = get_switches(session)
            if not switches:
                print("No connected switches found.")

            for device_id in switches:
                for statistic in get_port_statistics(session, device_id):
                    for port in statistic.get("ports", []):
                        port_id = port["port"]
                        current_bytes = port["bytesReceived"] + port["bytesSent"]
                        key = (device_id, port_id)
                        now = time.monotonic()
                        bandwidth = calculate_bandwidth(
                            current_bytes, previous_counters.get(key)
                        )
                        previous_counters[key] = (current_bytes, now)

                        if bandwidth is None:
                            continue

                        print(f"{device_id} port {port_id}: {bandwidth:.4f} Mbps")
                        if bandwidth > THRESHOLD_MBPS and device_id not in blocked_switches:
                            block_icmp(session, device_id)
                            blocked_switches.add(device_id)
                            print(f"ICMP policy installed on {device_id}.")

        except requests.exceptions.RequestException as error:
            print(f"ONOS request failed: {error}")
        except (KeyError, TypeError, ValueError) as error:
            print(f"Unexpected ONOS response: {error}")

        time.sleep(POLL_INTERVAL)


def main():
    if THRESHOLD_MBPS < 0 or POLL_INTERVAL <= 0:
        raise ValueError("THRESHOLD_MBPS must be nonnegative and POLL_INTERVAL positive.")
    try:
        monitor(create_session())
    except KeyboardInterrupt:
        print("\nNetwork policy monitor stopped.")


if __name__ == "__main__":
    main()
