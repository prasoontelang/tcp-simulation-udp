import getopt
from socket import *
from sys import *
import random
from time import *
import select
import getopt
import operator


serverName = '127.0.0.1' #
serverPort = 12345
init = t = time()
cwnd = 1
no_of_pkts = 26 # #######################
index = 0
timeout = 1 # ######################
seq_array = [] #stores the sequence no for each alphabet

argv = argv[1:]
try:
	   opts, args = getopt.getopt(argv,"N:p:t:s:")
except getopt.GetoptError:
		print 'asn3.py -N <Number of pkts> -t <time out> -p <server_port_no> -s <Server_IP>'
	        exit(2)
for opt, arg in opts:
	        if opt == '-h':
	 	       print 'asn2.py -i <IP_address> -t <Attachment_text> -p <Attachment_image> -r <Recipient> -s <Sender> -d <data>'
	               exit()
	        elif(opt in ("-N")):
	               no_of_pkts = int(arg)
	        elif(opt in ("-t")):
	             timeout = int(arg)
		elif(opt in ("-p")):
				 serverPort = int(arg)
		elif(opt in ("-s")):
	    	    serverName = arg

		
def pksend(pkt_snd):  #for sending a pkt to server
    print "SENT: "+pkt_snd
    clientSocket.sendto(pkt_snd, server)

def pkrecv(): #for receiving a pkt from server
    return clientSocket.recvfrom(300)

def pkgen(ch, index): #for generating pkt
    if alpha_use[index] == 0:
	    strlen = random.randint(1,100)
	    alpha_use[index] = strlen
    else:
        strlen = alpha_use[index]
    pkt_snd = [ch for x in range(strlen)] #array of characters
    pkt_snd = "".join(pkt_snd) #concatenating all characters to generate string
    index += 1
    return pkt_snd, index, strlen


def TIME():  #to display time for each pkt sent and received
    t = time()
    return t-init

def lost_index(seq_array,rcvd_ack): #to find the corresponding alphabet using sequence number
	for x in range(0,no_of_pkts):
		if rcvd_ack == seq_array[x]:
			return x

alpha_use = [0 for x in range(no_of_pkts)] #keeps track of no. of alphabets

server = serverName, serverPort
clientSocket = socket(AF_INET, SOCK_DGRAM)

seq = random.randint(1, 1000)
ack = 1
cnt = 1
pkt_snd = "seq="+str(seq)+";ack=1;S=1;len=0"
pksend(pkt_snd)
print "SENT TIME: "+str(TIME())


pkt_rcv, serverAddress = pkrecv()
print "RCVD: "+pkt_rcv
print "RCVD TIME: "+str(TIME())

pkt_rcv = pkt_rcv.split(';')
if pkt_rcv[2] == "SA=1":
    ack = int(pkt_rcv[0].partition('=')[2])
    rcvd_ack = int(pkt_rcv[1].partition('=')[2])
    prev_rcvd_ack = rcvd_ack
    seq = seq+1
    pkt_snd = "seq="+str(seq)+";ack="+str(ack)+";A=1;len=0" # ########################
    pksend(pkt_snd)
    print "CONNECTION GENERATED: "+str(TIME())
    seq = seq+1

    ch = chr(operator.mod(index, 26)+65)
    pkt_snd, index, strlen = pkgen(ch, index)
    pksend("seq="+str(seq)+";ack="+str(ack)+";A=1;len="+str(strlen)+";data="+pkt_snd)
    print "PKT SENT TIME: "+str(TIME())
    seq_array.append(seq)
    seq = seq + strlen
    seq_array.append(seq)
    
    flag = True
    while cwnd: # #########################
		temp = cwnd
		while temp:
			ready = select.select([clientSocket],[],[],timeout)
			print "\n\n\n"
			if ready[0]:
				pkt_rcv, serverAddress = pkrecv()
				print "RCVD: "+pkt_rcv
				print "PKT RCVD TIME: "+str(TIME())
				pkt_rcv = pkt_rcv.split(';')
				ack = int(pkt_rcv[0].partition('=')[2])
				rcvd_ack = int(pkt_rcv[1].partition('=')[2])
				temp -= 1
				if rcvd_ack==prev_rcvd_ack and flag:
					cnt = cnt+1
					if cnt==3:
						cwnd = cwnd/2
						temp = cwnd # for triple duplicate acks, cwnd is halved
						print "\n\n*********Received triple duplicate ACKs*********\n\n"
						cnt = 1
						flag = False
						index = lost_index(seq_array, rcvd_ack)
						seq= seq_array[index]
				elif rcvd_ack != prev_rcvd_ack:
					flag= True
				prev_rcvd_ack = rcvd_ack

				if index == no_of_pkts:
                                        print "Packets delivered"# do nothing, wait for server to send all acks
				else:	
					ch = chr(operator.mod(index, 26)+65)
					pkt_snd, index, strlen = pkgen(ch, index)
					pksend("seq="+str(seq)+";ack="+str(ack)+";A=1;len="+str(strlen)+";data="+pkt_snd)
					print "PKT SENT TIME: "+str(TIME())
					seq = seq + strlen
					if seq not in seq_array:
						seq_array.append(seq)

				if index == no_of_pkts:
#					print "\nCONNECTION IS CLOSING!!" # ############## Condition start from here
					pkt_snd = "seq="+str(seq)+";ack="+str(ack)+";F=1;len=0"
					pksend(pkt_snd)
					seq = seq+1
					pkt_rcv, serverAddress = pkrecv()
					print "RCVD: "+pkt_rcv
					pkt_rcv = pkt_rcv.split(';')
					#if seq == int(pkt_rcv[1].partition('=')[2]):
					if pkt_rcv[2] == "F=1":
						pkt_rcv, serverAddress = pkrecv()
						print "RCVD: "+pkt_rcv
						pkt_rcv = pkt_rcv.split(';')
						if pkt_rcv[2] == "F=1":
							pkt_snd = "seq="+pkt_rcv[1].partition('=')[2]+";ack="+str(int(pkt_rcv[0].partition('=')[2]))+";len=0"
							pksend(pkt_snd)
							clientSocket.close()
							exit()                            # #########################
				else:
					ch = chr(operator.mod(index, 26)+65)
					pkt_snd, index, strlen = pkgen(ch, index)
					pksend("seq="+str(seq)+";ack="+str(ack)+";A=1;len="+str(strlen)+";data="+pkt_snd)
					print "PKT SENT TIME: "+str(TIME())
					seq = seq + strlen
					if seq not in seq_array:
						seq_array.append(seq)
			else:
				index = lost_index(seq_array, rcvd_ack)
				ch = chr(operator.mod(index,26)+65)
				print "ACK not received for", ch, "at time ",TIME()
				pkt_snd, index, strlen = pkgen(ch, index)
				seq = seq_array[index]
				pksend("seq="+str(seq)+";ack="+str(ack)+";A=1;len="+str(strlen)+";data="+pkt_snd)

		cwnd = 2*cwnd
