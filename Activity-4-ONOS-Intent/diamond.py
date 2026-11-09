from mininet.topo import Topo

class DiamondTopo(Topo):
    def build(self):
        # Hosts with MAC addresses specified in the assignment
        h1 = self.addHost('h1', mac='00:00:00:00:00:01',
                         ip='10.0.0.1/8')
        h2 = self.addHost('h2', mac='00:00:00:00:00:02',
                         ip='10.0.0.2/8')

        # Four OpenFlow switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        # Host connections
        self.addLink(h1, s1)
        self.addLink(s4, h2)

        # Two independent paths
        self.addLink(s1, s2)
        self.addLink(s2, s4)
        self.addLink(s1, s3)
        self.addLink(s3, s4)

topos = {'diamond': (lambda: DiamondTopo())}
