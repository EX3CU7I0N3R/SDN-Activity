# Activity 2: Broadcast Storm Protection

An ONOS packet processor learns source MAC addresses and connection points, floods broadcasts, and blocks identical broadcast frames observed on the same device within a three-second window. Known unicast destinations receive temporary forwarding rules; duplicate broadcasts receive temporary drop rules.

## Requirements

- Java 17
- Maven
- An ONOS 3.0.0-SNAPSHOT build with its matching API artifacts available to Maven
- OpenFlow devices connected to ONOS

## Build

```bash
mvn clean package
```

The OSGi bundle is written to `target/broadcast-guard-1.0-SNAPSHOT.jar`. Install it using the ONOS application command appropriate to your controller build, then check the ONOS application list and logs to confirm activation.

## Notes

The duplicate key includes the device, source MAC, EtherType, and serialized frame hash. This is a classroom storm-protection demonstration: repeated identical broadcasts inside the window are suppressed, even if they are legitimate application traffic. Review the duplicate window and forwarding behavior for the topology before deploying outside a lab.
