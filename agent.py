import pickle
import socket
import threading
import time
import pseudoTreeGeneration
import message
import UTILMessagePropagation
import VALUEMessagePropagation
import numpy as np
import constants as consts

class DiscoveredAgent:
    def __init__(self, id, addr, port):
        self.id     = id
        self.addr   = addr
        self.port   = port
        self.domain = None
        self.varsFromStartingPoint = None

        self.isProducingPower      = False
        self.otherAgentsInfluence  = {}

    def getVarsFromStartingPoint(self, x):
        if not self.varsFromStartingPoint:
            return {'status': False,
                    'vars'  : np.array([0] * consts.kTIME_SLOTS) }

        vars = self.varsFromStartingPoint[x]

        return {'status'    : vars['status'],
                'vars'      : np.array(vars['vars']) }

    def getAvailPowerFromStartingPoint(self, x, other_agent):
        if not self.varsFromStartingPoint:
            return {'status': False,
                    'vars'  : np.array([0] * consts.kTIME_SLOTS) }

        vars = np.array( self.varsFromStartingPoint[x]['vars'] )

        # Le mie variabili sono negative, in quanto immetto potenza nel sistema,
        # sommo quindi le potenze degli altri agenti che ho già considerato.
        # Se la somma è positiva, allora la metto a 0, altrimenti lascio il valore.
        # In relations poi verrà aggiunto anche il contributo dell'agente considerato
        for id in self.otherAgentsInfluence:
            if id != other_agent:
                a = self.otherAgentsInfluence[id]
                vars = np.array(vars) + a.getVarsFromStartingPoint(x)['vars']

        vars[np.where(vars > 0)] = 0

        return {'status': True,
                'vars'  : np.array(vars)}

class Agent:
    def __init__(self, i, domain, port):
        # Informazioni per la comunicazione

        # Broadcast
        self.broadcast_addr = "127.0.0.1"
        self.broadcast_port = 12345

        # DPOP
        self.host = "127.0.0.1"
        self.port = port

        # Variabili Agente
        self.name               = "Agent"
        self.isListening        = False
        self.id                 = i
        self.domain             = domain
        self.relationWithParent = {}
        self.otherAgents        = {}
        self.isRoot             = True
        self.rootID             = 1
        self.value              = None
        self.isProducingPower   = False

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
    Ritorna una lista contente il ciclo che questo agente
    vorrebbe effettuare
    """
    def getCycle(self):
        raise NotImplementedError("Questo metodo deve essere implementato da ogni agente")

    """
    L'output è una tupla il cui primo elemento indica se l'assegnazione e fattibile, mentre il secondo
    contiene l'assegnazione vera e propria. In caso di assegnazione NON fattibile, tutte le variabili saranno
    uguali a 0
    OUTPUT (feasible, result)
    """
    def getVarsFromStartingPoint(self, x):
        raise NotImplementedError("Questo metodo deve essere implementato da ogni agente")

    """
    Prende tutti i possibili punti di inizio e crea un dict che li contiene. Questo dict
    sarà poi mandato a tutti gli altri agenti durante la creazione dello pseudoTree
    """
    def getVarsFromAllStartingPoints(self):
        all_vars = {}
        for t in range(0, consts.kTIME_SLOTS):
            all_vars[t] = self.getVarsFromStartingPoint(t)
        return all_vars

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

    def addNewDiscoveredAgent(self, id, addr, port, isProducingPower = False):
        discovered = DiscoveredAgent(id, addr, port)
        discovered.isProducingPower = isProducingPower
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
        #self.debug("[INVIO] {} -> {}: {} {}".format(self.id, dest_node_id, type, data))

        pdata = pickle.dumps( (self.id, type, data) )

        dest = self.otherAgents[ dest_node_id ]

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect( (dest.addr, dest.port) )
            res = sock.sendall( pdata )
        except:
            time.sleep(0.1)
            sock.close()
            self.sendMsg(dest_node_id, type, data)
        finally:
            sock.close()

    def listenToMessages(self):
        listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        listening_socket.bind( (self.host, self.port) )

        self.isListening = True

        listening_socket.listen(1)

        while (True):
            connection, client_address = listening_socket.accept()
            connection.settimeout(60)

            threading.Thread(target  = self.handleArrivedMsg, kwargs = {'connection' : connection} ).start()


        self.isListening = False

    def handleArrivedMsg(self, connection):
        data = bytearray()

        # Receive the data in small chunks
        try:
            while True:
                tmp_data = connection.recv(16)
                data += tmp_data
                if not tmp_data:
                    break
        finally:
            connection.close()

        udata = pickle.loads(data)

        msg_sender = udata[0]
        msg_type = udata[1]
        msg_value = udata[2]

        # self.debug("[RICEZIONE] ({}, {}): {}".format(int(msg_sender), str(msg_type), msg_value))
        self.msgs[(int(msg_sender), str(msg_type))] = message.Message(msg_type, msg_sender, msg_value)

        # self.debug( self.msgs )

    def debug(self, text):
        print("[{} {}]: {}".format(self.name, self.id, text))

    def start(self):
        self.listenToMessagesThread = threading.Thread(name='ListenToMessages-Thread-of-Agent-' + str(self.id),
                                                       target=self.listenToMessages
                                                       )
        self.listenToMessagesThread.setDaemon(True)
        self.listenToMessagesThread.start()

        while (not self.isListening):
            time.sleep(0.5)

        self.debug("Avviato")

        # Avvio la procedura per la creazione dello pseudo-tree
        pseudoTreeGeneration.start( self )

        # Resetto il contenuto del dict messaggi
        self.msgs = {}

        # Avvio la procedura di propagazione dei messaggi di UTIL
        UTILMessagePropagation.start( self )

        # Solamente gli agenti NON root devono attendere il messaggio di VALUE
        # dal loro genitore
        if not self.isRoot:
            VALUEMessagePropagation.start( self )