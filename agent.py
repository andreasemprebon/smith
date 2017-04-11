import pickle
import socket
import threading
import time
import os
import pseudoTreeGeneration
import message
import UTILMessagePropagation

kTIME_SLOTS = 96

class DiscoveredAgent:
    def __init__(self, id, addr, port):
        self.id     = id
        self.addr   = addr
        self.port   = port
        self.domain = None

class Agent:
    def __init__(self, i, domain, port):
        # Informazioni per la comunicazione

        # Broadcast
        self.broadcast_addr = "127.0.0.1"
        self.broadcast_port = 12345

        # DPOP
        self.host = "127.0.0.1"
        self.port = port

        # Variabili da controllare, sono i vari time slots
        self.vars = [0] * kTIME_SLOTS

        # Variabili Agente
        self.isListening    = False
        self.id             = i
        self.domain         = domain
        self.relations      = {}
        self.otherAgents    = {}
        self.isRoot         = True
        self.rootID         = 1

        self.p  = None  # The parent's id
        self.pp = None  # A list of the pseudo-parents' ids
        self.c  = None  # A list of the childrens' ids
        self.pc = None  # A list of the pseudo-childrens' ids

        self.msgs = {}  # The dict where all the received messages are stored


        # Inizia ad annunciarti e ad ascoltare annunci sulla rete
        # self.annouceThread = threading.Thread(  name    = 'Announcing-Thread-of-Agent-' + str( self.id ),
        #                                         target  = self.announceMyselfInTheNetwork,
        #                                         kwargs  = { 'myself' : self }
        #                                         )
        #
        # self.readAnnouncementThread = threading.Thread( name    = 'Read-Announcement-Thread-of-Agent-' + str(self.id),
        #                                                 target  = self.getOtherAgentsAnnouncement,
        #                                                 kwargs  = { 'myself': self }
        #                                                 )

        # self.annouceThread.setDaemon(True)
        # self.readAnnouncementThread.setDaemon(True)


        # Non si puo' fare sulla stessa macchina perche' non posso aprire piu' socket sulla stessa porta, ma in generale
        # quando l'intero sistema sara' distribuito funzionera'
        #self.annouceThread.start()
        #self.readAnnouncementThread.start()

        # Inizio ad ascoltare i messaggi in arrivo sulla mia porta

    """
    Se un nodo e' foglia, non ha figli, quindi vero se il numero di figli
    e' uguale a zero, falso altrimenti
    """
    def isLeaf(self):
        if self.c is None:
            self.debug("[WARNING] Albero NON ancora inizializzato.")
            return False
        return len(self.c) == 0

    """
    Invia periodicamente un messaggio in broadcast sulla rete in modo da annunciare la sua presenza
    Il messaggio contiene il proprio indirizzo IP e la porta utilizzata per ricevere i messaggi di DPOP
    """
    def announceMyselfInTheNetwork(self, myself):
        raise NotImplementedError
        # pdata = pickle.dumps((myself.id, myself.host, myself.port))
        # sock  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #
        # while (True):
        #     #print("Annuncio Agente {}".format(myself.id))
        #     sock.sendto(pdata, (myself.broadcast_addr, myself.broadcast_port) )
        #     time.sleep(5)
        #
        # sock.close()

    # @TODO: Funzione da terminare, quando sara' effettivamete tutto distribuito
    def getOtherAgentsAnnouncement(self, myself):
        raise NotImplementedError
        # listening_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        #
        # listening_socket.bind( (myself.host, myself.broadcast_port) )
        #
        # while (True):
        #     data, addr = listening_socket.recvfrom(65536)
        #     udata = pickle.loads(data)
        #     print(udata)
        #
        #     agent_id    = udata[0]
        #     agent_addr  = udata[1]
        #     agent_port  = udata[2]
        #
        #     if agent_id != myself.id:
        #         if agent_id not in myself.otherAgents:
        #             self.addNewDiscoveredAgent(agent_id, agent_addr, agent_port)
        #
        # listening_socket.close()

    def addNewDiscoveredAgent(self, id, addr, port):
        discovered = DiscoveredAgent(id, addr, port)
        self.otherAgents[ id ] = discovered

    """
    Calcola il valore dell'utility secondo i bindings correnti
    """
    def computeUtil(self):
        raise NotImplementedError

    """
    Invia i messaggi tramite il protocollo UDP:
        dest_node_id:   id nodo dell'Agente destinatario
        title:          titolo del messaggio
        data:           payload del messaggio
    """
    def sendMsg(self, dest_node_id, type, data, ):
        self.debug("[INVIO] {} -> {}: {} {}".format(self.id, dest_node_id, type, data))

        pdata = pickle.dumps( (self.id, type, data) )

        dest = self.otherAgents[ dest_node_id ]

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(pdata, (dest.addr, dest.port))
        sock.close()

    def listenToMessages(self):
        listening_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        listening_socket.bind( (self.host, self.port) )

        self.isListening = True

        while (True):
            data, addr = listening_socket.recvfrom(65536)
            udata = pickle.loads(data)

            msg_sender  = udata[0]
            msg_type    = udata[1]
            msg_value   = udata[2]

            self.debug( "[RICEZIONE] ({}, {}): {}".format(int(msg_sender), str(msg_type), msg_value ) )
            self.msgs[ (int(msg_sender), str(msg_type)) ] = message.Message(msg_type, msg_sender, msg_value)

            self.debug( self.msgs )

        self.isListening = False
        listening_socket.close()

    def debug(self, text):
        print("[Agent {}]: {}".format(self.id, text))

    def start(self):
        self.listenToMessagesThread = threading.Thread(name='ListenToMessages-Thread-of-Agent-' + str(self.id),
                                                       target=self.listenToMessages
                                                       )
        self.listenToMessagesThread.setDaemon(True)
        self.listenToMessagesThread.start()

        while (not self.isListening):
            time.sleep(0.5)

        self.debug("Avviato")
        pseudoTreeGeneration.start( self )
        UTILMessagePropagation.start( self )

a1 = Agent(1, range(0, 96), 12346)
a2 = Agent(2, range(0, 96), 12347)
a3 = Agent(3, range(0, 96), 12348)

a2.isRoot = False
a3.isRoot = False

a1.addNewDiscoveredAgent(a2.id, "127.0.0.1", a2.port)
a1.addNewDiscoveredAgent(a3.id, "127.0.0.1", a3.port)

a2.addNewDiscoveredAgent(a1.id, "127.0.0.1", a1.port)
a2.addNewDiscoveredAgent(a3.id, "127.0.0.1", a3.port)

a3.addNewDiscoveredAgent(a1.id, "127.0.0.1", a1.port)
a3.addNewDiscoveredAgent(a2.id, "127.0.0.1", a2.port)

# while (not a1.isListening):
#     time.sleep(0.5)
#
# while (not a2.isListening):
#     time.sleep(0.5)
#
# while (not a3.isListening):
#     time.sleep(0.5)

"""
Avvio i vari agenti sulla stessa macchina
E' solamente il genitore che lancia, quindi mi salvo
in parent_pid il valore del PID del processo attuale in modo
che sia solo lui a fare la fork
"""
parent_pid = os.getpid()

children = []

#Avvio il primo processo figlio
if parent_pid == os.getpid():
    childid = os.fork()
    children.append(childid)
    if childid == 0:
        a2.start()

#Avvio il secondo processo figlio
if parent_pid == os.getpid():
    childid = os.fork()
    children.append(childid)
    if childid == 0:
        a3.start()

#Avvio il padre ed attendo che tutti i figli termino
if parent_pid == os.getpid():
    a1.start()
    for i in children:
        os.wait()