tcp-simulation-udp
==================

*UDP acting like TCP with the help of application layer*

This program using the UDP protocol simulates TCP properties such as Triple-Duplicate ACK, Timeout
and fast re-transmission between a UDP server and a UDP client.

### How it works?

To start UDP server:

`python UDPserver.py`

The ip address used is that of local host and port number is 12345

To start UDP client:

`python UDPclient.py -N <Number of pkts> -t <time out> -p <server_port_no> -s <Server_IP>`

By default the number of packets are 26, timeout is 1 second, server port number is 12345 and server IP
is localhost.

In the client side, data is automatically generated and certain parameters such as
SYN, ACK, SYN-ACK, SEQ and DATA with appropriate values are prefixed to the generated data and sent
to the server as a string.
The server parses the received string, compares the sequence number with the ack. If the sequence number
and the previous ack matches, the server sends an updated ACK. If there is a mismatch between the sequence
number and the ack, it sends back a `duplicate ACK` to the client. The client on receiving
`Triple Duplicate ACKs` resends the data which has not been received by the server.

In the client side, for every orderly ACK received, the client doubles the window size for gaining full
efficiency of the transfer link. If there is a packet loss, the client will not receive an ACK for the
lost packets. This will cause `Timeout` and the client will then reduce the window size by half and
resend the packets whose ACK was not received sequentially.

On successful data transfer, the client side will request for connection termination using FIN bit.
The server will send an ACK and will also send a FIN bit after the ACK. When the client side receives
the FIN from the server, it will send an ACK to the server and terminate the connection.
