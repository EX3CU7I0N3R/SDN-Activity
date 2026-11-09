# Activity 2: Broadcast Storm Protection using ONOS

## Objective
To develop an ONOS application that detects duplicate broadcast packets and helps prevent unnecessary broadcast traffic in an SDN network.

## Implementation
The BroadcastGuard application uses an ONOS packet processor to:

- Intercept incoming packets.
- Learn source MAC addresses and their switch connection points.
- Maintain a MAC learning table.
- Detect duplicate broadcast packets within a configured time window.
- Block duplicate broadcasts.
- Install temporary flow rules to drop repeated packets.
- Forward packets when the destination MAC address is known.

## Technologies
- Java
- ONOS Controller 3.0.0-SNAPSHOT
- Maven
- OSGi Declarative Services
- OpenFlow

## Configuration
The project uses Maven and ONOS API dependencies.

Build the application using:

```bash
mvn clean package
