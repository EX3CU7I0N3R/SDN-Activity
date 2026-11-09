
package org.onosproject.broadcastguard;

import org.osgi.service.component.annotations.Activate;
import org.osgi.service.component.annotations.Component;
import org.osgi.service.component.annotations.Deactivate;
import org.osgi.service.component.annotations.Reference;

import org.onlab.packet.Ethernet;
import org.onlab.packet.MacAddress;
import org.onosproject.core.ApplicationId;
import org.onosproject.core.CoreService;
import org.onosproject.net.ConnectPoint;
import org.onosproject.net.DeviceId;
import org.onosproject.net.PortNumber;
import org.onosproject.net.flow.DefaultFlowRule;
import org.onosproject.net.flow.DefaultTrafficSelector;
import org.onosproject.net.flow.DefaultTrafficTreatment;
import org.onosproject.net.flow.FlowRule;
import org.onosproject.net.flow.FlowRuleService;
import org.onosproject.net.flow.TrafficSelector;
import org.onosproject.net.packet.PacketContext;
import org.onosproject.net.packet.PacketPriority;
import org.onosproject.net.packet.PacketProcessor;
import org.onosproject.net.packet.PacketService;

import java.util.Arrays;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Component(immediate = true)
public class BroadcastGuard {

    private static final int PROCESSOR_PRIORITY = 2;
    private static final int FLOW_PRIORITY = 40000;
    private static final int DROP_PRIORITY = 50000;

    private static final long DUPLICATE_WINDOW_MS = 3000;
    private static final int DROP_TIMEOUT_SECONDS = 3;
    private static final int FORWARD_TIMEOUT_SECONDS = 30;

    @Reference
    protected CoreService coreService;

    @Reference
    protected PacketService packetService;

    @Reference
    protected FlowRuleService flowRuleService;

    private ApplicationId appId;
    private InternalPacketProcessor processor;

    // MAC address -> switch and port where the MAC was learned
    private final Map<MacAddress, ConnectPoint> macTable =
            new ConcurrentHashMap<>();

    // Recent broadcast packet fingerprints and their timestamps
    private final Map<String, Long> recentBroadcasts =
            new ConcurrentHashMap<>();

    private final TrafficSelector packetSelector =
            DefaultTrafficSelector.builder().build();

    @Activate
    protected void activate() {

        appId = coreService.registerApplication(
                "org.onosproject.broadcastguard");

        processor = new InternalPacketProcessor();

        packetService.addProcessor(processor, PROCESSOR_PRIORITY);

        packetService.requestPackets(
                packetSelector,
                PacketPriority.CONTROL,
                appId);

        System.out.println("BroadcastGuard started successfully.");
    }

    @Deactivate
    protected void deactivate() {

        packetService.removeProcessor(processor);

        packetService.cancelPackets(
                packetSelector,
                PacketPriority.CONTROL,
                appId);

        macTable.clear();
        recentBroadcasts.clear();

        System.out.println("BroadcastGuard stopped.");
    }

    private class InternalPacketProcessor
            implements PacketProcessor {

        @Override
        public void process(PacketContext context) {

            if (context.isHandled()) {
                return;
            }

            Ethernet ethernet = context.inPacket().parsed();

            if (ethernet == null) {
                return;
            }

            ConnectPoint ingress =
                    context.inPacket().receivedFrom();

            DeviceId deviceId = ingress.deviceId();
            PortNumber ingressPort = ingress.port();

            MacAddress srcMac = ethernet.getSourceMAC();
            MacAddress dstMac = ethernet.getDestinationMAC();

            short etherType = ethernet.getEtherType();

            System.out.println(
                    "PacketIn: EtherType=" + etherType
                    + ", Source=" + srcMac
                    + ", Destination=" + dstMac);

            // Learn the source MAC address.
            macTable.put(srcMac, ingress);

            // Handle broadcast packets separately.
            if (ethernet.isBroadcast()) {

                handleBroadcast(
                        context,
                        ethernet,
                        deviceId,
                        ingressPort,
                        srcMac,
                        dstMac,
                        etherType);

                return;
            }

            // Look up the destination MAC address.
            ConnectPoint destination = macTable.get(dstMac);

            // Unknown destination: flood the packet.
            if (destination == null
                    || !destination.deviceId().equals(deviceId)) {

                System.out.println(
                        "Unknown destination. Flooding packet.");

                floodPacket(context);
                return;
            }

            // Avoid forwarding a packet back through its input port.
            if (destination.port().equals(ingressPort)) {
                context.block();
                return;
            }

            // Known destination: install a reactive forwarding rule.
            System.out.println(
                    "Known destination. Installing forwarding rule.");

            installForwardingRule(
                    deviceId,
                    ingressPort,
                    dstMac,
                    destination.port());

            // Forward the packet that triggered the PacketIn event.
            context.treatmentBuilder()
                    .setOutput(destination.port());

            context.send();
        }
    }

    private void handleBroadcast(
            PacketContext context,
            Ethernet ethernet,
            DeviceId deviceId,
            PortNumber ingressPort,
            MacAddress srcMac,
            MacAddress dstMac,
            short etherType) {

        // Fingerprint the complete Ethernet frame.
        byte[] frame = ethernet.serialize();
        int fingerprint = Arrays.hashCode(frame);

        String key = deviceId + ":"
                + srcMac + ":"
                + etherType + ":"
                + fingerprint;

        long now = System.currentTimeMillis();

        Long previous = recentBroadcasts.put(key, now);

        if (previous != null
                && now - previous < DUPLICATE_WINDOW_MS) {

            System.out.println(
                    "Duplicate broadcast detected. Blocking packet.");

            context.block();

            installBroadcastDropRule(
                    deviceId,
                    ingressPort,
                    srcMac,
                    dstMac,
                    etherType);

            return;
        }

        System.out.println(
                "First broadcast packet. Flooding packet.");

        floodPacket(context);
    }

    private void floodPacket(PacketContext context) {

        context.treatmentBuilder()
                .setOutput(PortNumber.FLOOD);

        context.send();
    }

    private void installForwardingRule(
            DeviceId deviceId,
            PortNumber ingressPort,
            MacAddress dstMac,
            PortNumber outputPort) {

        TrafficSelector selector =
                DefaultTrafficSelector.builder()
                        .matchInPort(ingressPort)
                        .matchEthDst(dstMac)
                        .build();

        FlowRule rule =
                DefaultFlowRule.builder()
                        .forDevice(deviceId)
                        .withSelector(selector)
                        .withTreatment(
                                DefaultTrafficTreatment.builder()
                                        .setOutput(outputPort)
                                        .build())
                        .withPriority(FLOW_PRIORITY)
                        .makeTemporary(FORWARD_TIMEOUT_SECONDS)
                        .fromApp(appId)
                        .build();

        flowRuleService.applyFlowRules(rule);
    }

    private void installBroadcastDropRule(
            DeviceId deviceId,
            PortNumber ingressPort,
            MacAddress srcMac,
            MacAddress dstMac,
            short etherType) {

        TrafficSelector selector =
                DefaultTrafficSelector.builder()
                        .matchInPort(ingressPort)
                        .matchEthSrc(srcMac)
                        .matchEthDst(dstMac)
                        .matchEthType(etherType)
                        .build();

        FlowRule dropRule =
                DefaultFlowRule.builder()
                        .forDevice(deviceId)
                        .withSelector(selector)
                        .withTreatment(
                                DefaultTrafficTreatment.builder()
                                        .drop()
                                        .build())
                        .withPriority(DROP_PRIORITY)
                        .makeTemporary(DROP_TIMEOUT_SECONDS)
                        .fromApp(appId)
                        .build();

        flowRuleService.applyFlowRules(dropRule);
    }
}

