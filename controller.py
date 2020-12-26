# Final Skeleton
#
# Hints/Reminders from Lab 3:
#
# To check the source and destination of an IP packet, you can use
# the header information... For example:
#
# ip_header = packet.find('ipv4')
#
# if ip_header.srcip == "1.1.1.1":
#   print "Packet is from 1.1.1.1"
#
# Important Note: the "is" comparison DOES NOT work for IP address
# comparisons in this way. You must use ==.
# 
# To send an OpenFlow Message telling a switch to send packets out a
# port, do the following, replacing <PORT> with the port number the 
# switch should send the packets out:
#
#    msg = of.ofp_flow_mod()
#    msg.match = of.ofp_match.from_packet(packet)
#    msg.idle_timeout = 30
#    msg.hard_timeout = 30
#
#    msg.actions.append(of.ofp_action_output(port = <PORT>))
#    msg.data = packet_in
#    self.connection.send(msg)
#
# To drop packets, simply omit the action.
#

from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

class Final (object):
  """
  A Firewall object is created for each switch that connects.
  A Connection object for that switch is passed to the __init__ function.
  """
  def __init__ (self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection

    # This binds our PacketIn event listener
    connection.addListeners(self)


  #helper function for sending out packets
  def send_out(self, packet, packet_in, port): #used flood from lab 3 as base
    # 1) send the original message 
    #of.ofp_packet_out(port = port)

    # 2) send message to controllerc
    msg = of.ofp_flow_mod()
    msg.match = of.ofp_match.from_packet(packet)
    msg.idle_timeout = 30
    msg.hard_timeout = 30
    msg.actions.append(of.ofp_action_output(port = port))
    msg.data = packet_in
    msg.buffer_id = packet_in.buffer_id
    self.connection.send(msg)

  #helper function for dropping packets
  def drop_out(self, packet, packet_in, port): #used drop from lab 3 as base
    # 1) send message to controller
    msg = of.ofp_flow_mod()
    msg.match = of.ofp_match.from_packet(packet)
    msg.idle_timeout = 30 #gets deleted after time if rule not applied
    msg.hard_timeout = 30 #gets deleted no matter what after time
    msg.data = packet_in
    #msg.buffer_id = packet_in.buffer_id
    self.connection.send(msg)


  def do_final (self, packet, packet_in, port_on_switch, switch_id):
    # This is where you'll put your code. The following modifications have 
    # been made from Lab 3:
    #   - port_on_switch: represents the port that the packet was received on.
    #   - switch_id represents the id of the switch that received the packet.
    #      (for example, s1 would have switch_id == 1, s2 would have switch_id == 2, etc...)
    # You should use these to determine where a packet came from. To figure out where a packet 
    # is going, you can use the IP header information.

    # use ports, switch id, source and destination id, protocols to differentiate
    
    deptA = ["10.1.1.10", "10.1.2.20", "10.1.3.30", "10.1.4.40"] #IP addresses in Floor 1 
    deptB = ["10.2.5.50", "10.2.6.60", "10.2.7.70", "10.2.8.80"] #IP addresses in Floor 2

    ip = packet.find('ipv4')

    #source and destination address from ip header
    #ip.srcip
    #ip.dstip

    if packet.find('icmp'):
      #untrusted host cant send icmp floor hosts or server
      if ip.srcip == "106.44.82.103" and (ip.dstip in deptA or ip.dstip in deptB or ip.dstip == "10.3.9.90"):
        self.drop_out(packet, packet_in, 7) #port doesn't matter since not used in drop
        print "drop_called" # for testing , deltet later
        return
      if ip.srcip == "108.24.31.112" and (ip.dstip in deptB or ip.dstip == "10.3.9.90"): #trusted can't send to server or deptB
        self.drop_out(packet, packet_in, 7) #port doesn't matter since not used in drop
        print "drop_called" # for testing , deltet later
        return
      if (ip.srcip in deptA and ip.dstip in deptB) or (ip.srcip in deptB and ip.dstip in deptA): #can't send between floors
        self.drop_out(packet, packet_in, 7) #port doesn't matter since not used in drop
        print "drop_called" # for testing , deltet later
        return

    if ip:
        #-----Floor switches--------------------------
        if switch_id == 11: #floor 1 switch 1
          if ip.dstip == "10.1.1.10": #h10
            self.send_out(packet, packet_in, 1) #outgoing port on switch (to h10)
            print "send_called" # for testing , deltet later
            return
          elif ip.dstip == "10.1.2.20": #h20
            self.send_out(packet, packet_in, 2) #outgoing port on switch (to h20)
            print "send_called" # for testing , deltet later
            return
          else:
            self.send_out(packet, packet_in, 3) #outgoing port on switch (to core switch)
            print "floor 1 switch 1"#for testing (delete later)
        if switch_id == 12: #floor 1 switch 2
          if ip.dstip == "10.1.3.30": #h30
            self.send_out(packet, packet_in, 1) #outgoing port on switch (to h30)
            print "send_called" # for testing , deltet later
            return
          elif ip.dstip == "10.1.4.40": #h40
            self.send_out(packet, packet_in, 2) #outgoing port on switch (to h40)
            print "send_called" # for testing , deltet later
            return
          else:
            self.send_out(packet, packet_in, 3) #outgoing port on switch (to core switch)
            print "send_called" # for testing , deltet later
            return
        if switch_id == 21: #floor 2 switch 1
          if ip.dstip == "10.2.5.50": #h50
            self.send_out(packet, packet_in, 1) #outgoing port on switch (to h50)
            print "send_called" # for testing , deltet later
            return
          elif ip.dstip == "10.2.6.60": #h60
            self.send_out(packet, packet_in, 2) #outgoing port on switch (to h60)
            print "send_called" # for testing , deltet later
            return
          else:
            self.send_out(packet, packet_in, 3) #outgoing port on switch (to core switch)
            print "send_called" # for testing , deltet later
            return
        if switch_id == 22: #floor 2 switch 2
          if ip.dstip == "10.2.7.70": #h70
            self.send_out(packet, packet_in, 1) #outgoing port on switch (to h70)
            print "send_called" # for testing , deltet later
            return
          elif ip.dstip == "10.2.8.80": #h80
            self.send_out(packet, packet_in, 2) #outgoing port on switch (to h80)
            print "send_called" # for testing , deltet later
            return
          else:
            self.send_out(packet, packet_in, 3) #outgoing port on switch (to core switch)
            print "send_called" # for testing , deltet later
            return

        #-----Data Center switch--------------------------
        if switch_id == 2: #floor 1 switch 1
          if ip.dstip == "10.3.9.90": #h_server
            self.send_out(packet, packet_in, 1) #outgoing port on switch (to h_server)
            print "data center"#for testing (delete later)
            print "send_called" # for testing , deltet later
            return
          else:
            self.send_out(packet, packet_in, 3) #outgoing port on switch (to core switch)
            print "send_called" # for testing , deltet later
            return

        #-----Core switch--------------------------
        if switch_id == 1: #core switch 
          if ip.srcip != "106.44.82.103" and (ip.dstip == "10.1.1.10" or ip.dstip == "10.1.2.20"): #if going to host 10 or host 20
            self.send_out(packet, packet_in, 1) #outgoing port on core switch (to floor 1 switch 1)
            print "send_called" # for testing , deltet later
            return
          elif ip.srcip != "106.44.82.103" and (ip.dstip == "10.1.3.30" or ip.dstip == "10.1.4.40"): #if going to host 30 or host 40
            self.send_out(packet, packet_in, 2) #outgoing port on core switch (to floor 1 switch 2)
            print "send_called" # for testing , deltet later
            return
          elif ip.srcip != "106.44.82.103" and (ip.dstip == "10.2.5.50" or ip.dstip == "10.2.6.60"): #if going to host 50 or host 60
            self.send_out(packet, packet_in, 3) #outgoing port on core switch (to floor 2 switch 1)
            print "send_called" # for testing , deltet later
            return
          elif ip.srcip != "106.44.82.103" and (ip.dstip == "10.2.7.70" or ip.dstip == "10.2.8.80"): #if going to host 70 or host 80
            self.send_out(packet, packet_in, 4) #outgoing port on core switch (to floor 2 switch 2)
            print "send_called" # for testing , deltet later
            return
          
          elif ip.srcip == "106.44.82.103" and ip.dstip == "10.3.9.90": #if going to untrusted host
            self.drop_out(packet, packet_in, 7) # blocked untrusted from sending packets to the server
            print "drop_called" # for testing , deltet later
            return
          elif ip.srcip == "108.24.31.112" and ip.dstip == "10.3.9.90": #if going to trusted host
            self.drop_out(packet, packet_in, 7) # blocked trusted from sending packets to the server
            print "drop_called" # for testing , deltet later
            return

          elif ip.dstip == "10.3.9.90": #if going to server
            self.send_out(packet, packet_in, 5) #outgoing port on core switch (to Data Center switch)
            print "core switch"#for testing (delete later)
            return

          elif ip.dstip == "108.24.31.112": #if going to trusted host
            self.send_out(packet, packet_in, 6) #outgoing port on core switch (to trusted host)
            print "send called" # for testing , deltet later
            return

          elif ip.dstip == "106.44.82.103": #if going to untrusted host
            self.send_out(packet, packet_in, 7) #outgoing port on core switch (to untrusted host)
            print "send called" # for testing , deltet later
            return

    else:
      self.send_out(packet, packet_in, of.OFPP_FLOOD)
      print "send called" # for testing , deltet later
      return

    #print "Example code."

  def _handle_PacketIn (self, event):
    """
    Handles packet in messages from the switch.
    """
    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp # The actual ofp_packet_in message.
    self.do_final(packet, packet_in, event.port, event.dpid)

def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Final(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
