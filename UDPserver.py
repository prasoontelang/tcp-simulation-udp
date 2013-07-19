import sys, getopt, random, select
from socket import *
from time import *

def pksend(pkt_snd):
    serverSocket.sendto(pkt_snd, clientAddr)
def pkrecv():
    return serverSocket.recvfrom(300)

serverName = ''
serverPort = 12345
seq = random.randint(1,1000)
loss_cnt = 0
prev_pkt = ''

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print "UDP Server ready to receive data"

pkt_rcv, clientAddr = pkrecv()
print pkt_rcv
pkt_rcv = pkt_rcv.split(';')
if pkt_rcv[2] == "S=1":
	ack = int(pkt_rcv[0].partition('=')[2])
	ack = ack+1
	respMsg = "seq="+str(seq)+";ack="+str(ack)+";SA=1;len=0"
	prev_pkt = respMsg
	seq = seq+1
	pksend(respMsg)
    
	pkt_rcv, clientAddr = pkrecv()
	pkt_rcv = pkt_rcv.split(';')
	if pkt_rcv[2] == "A=1":
		print "The connection is established!!"
		old_seq = ack
		ack = ack+1
		prev_ack =  ack     
        while 1:
			ready = select.select([serverSocket],[],[],3)
			if ready[0]:
				pkt_rcv, clientAddr = pkrecv()

				fin = pkt_rcv.split(';')
				if fin[2]== "F=1":
					#ack = ack+1
					fin_ack = int(fin[0].partition('=')[2])+1
					seq = int(fin[1].partition('=')[2])
					pkt_snd = "seq="+str(seq)+";ack="+str(fin_ack)+";F=1;len=0"
					pksend(pkt_snd)
					#seq = seq+1
					pkt_snd = "seq="+str(seq)+";ack="+str(fin_ack)+";F=1;len=0"
					pksend(pkt_snd)
					fin, clientAddr = pkrecv()
					fin = fin.split(';')
					seq = seq+1
					if int(fin[1].partition('=')[2]) == seq: 
						serverSocket.close()
						exit()

				elif loss_cnt != 4:
					print pkt_rcv
					pkt = pkt_rcv.split(';')
					new_seq = int(pkt[0].partition('=')[2])
					if prev_ack<new_seq: 
						pksend(prev_pkt)				
						continue
					elif prev_ack>new_seq:
						continue
					ack = ack + int(pkt[3].partition('=')[2])
					respMsg = "seq="+str(seq)+";ack="+str(ack)+";A=1;len=0"
					loss_cnt= loss_cnt+1
					if loss_cnt == 6: #random.randint(5,10):
						print "This packet is delayed"
						loss_cnt = 0
						sleep(5)
					if old_seq<new_seq:
						pksend(respMsg)
					prev_pkt = respMsg
					prev_ack = ack
					old_seq = new_seq
				else:
					loss_cnt += 1


	else:
				print "Connection establishment failed!!"	

serverSocket.close()
