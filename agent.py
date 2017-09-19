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
import os
import sys
import json
from subprocess import check_output

class DiscoveredAgent:
    def __init__(self, id, addr, port):
        self.id     = id
        self.addr   = addr
        self.port   = port
        self.domain = None
        self.varsFromStartingPoint = None
        self.timeOfDiscovery = time.time()

        self.optimizableAgent      = True
        self.isProducingPower      = False
        self.otherAgentsInfluence  = {}

    def getVarsFromStartingPoint(self, x):
        if not self.optimizableAgent:
            return {'status': True,
                    'vars'  : np.zeros( consts.kTIME_SLOTS )}

        if not self.varsFromStartingPoint:
            return {'status': False,
                    'vars'  : np.array([0] * consts.kTIME_SLOTS) }

        vars = self.varsFromStartingPoint[x]

        return {'status'    : vars['status'],
                'vars'      : np.array(vars['vars']) }

    def getAvailPowerFromStartingPoint(self, x, other_agent):
        if not self.optimizableAgent:
            return {'status': True,
                    'vars'  : np.zeros( consts.kTIME_SLOTS )}

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
    def __init__(self, i, domain, port, simulation = False):
        # Attendo di essere connesso ad una rete Wireless nota
        waitingForWiFi = True
        while (waitingForWiFi):
            print("In attesa di collegamento alla rete...")
            scanoutput = check_output(["iwlist", "wlan0", "scan"])

            for line in scanoutput.split():
                line = line.decode("utf-8")
                if line[:5] == "ESSID":
                    ssid = line.split('"')[1]
                    if ssid == "FASTWEB-1-AF8BCD" or ssid == "FASTWEB-1-0021965C8A34":
                        print("Collegato alla rete {}".format(ssid))
                        waitingForWiFi = False
                        break
            time.sleep(1.0)

        # Informazioni per la comunicazione

        # Broadcast
        self.broadcast_addr = "255.255.255.255"
        self.broadcast_port = 5555
        self.broadcast_web_port = 5556

        # DPOP
        if simulation:
            self.host = "127.0.0.1"
        else:
            self.host = self.getIPAddress()

        self.port = port

        self.killStartThread    = False
        self.jsonConfiguration  = None

        # Variabili Agente
        self.name               = "Agent"
        self.isListening        = False
        self.id                 = i
        self.domain             = domain
        self.relationWithParent = {}
        self.otherAgents        = {}
        self.isRoot             = True
        self.rootID             = self.id
        self.value              = None
        self.isProducingPower   = False
        self.optimizableAgent   = True

        self.p  = None  # The parent's id
        self.pp = None  # A list of the pseudo-parents' ids
        self.c  = None  # A list of the childrens' ids
        self.pc = None  # A list of the pseudo-childrens' ids

        self.msgs = {}  # The dict where all the received messages are stored

        ### PERFORMANCE
        self.messages_sent_total_size = 0 #bytes
        self.messages_sent_number     = 0

        if not simulation:
            # Inizia ad annunciarti e ad ascoltare annunci sulla rete
            self.annouceThread = threading.Thread(  name    = 'Announcing-Thread-of-Agent-' + str( self.id ),
                                                    target  = self.announceMyselfInTheNetwork,
                                                    kwargs  = { 'myself' : self }
                                                    )

            self.readAnnouncementThread = threading.Thread( name    = 'Read-Announcement-Thread-of-Agent-' + str(self.id),
                                                            target  = self.getOtherAgentsAnnouncement,
                                                            kwargs  = { 'myself': self }
                                                            )

            self.replyToRequestFromWebServerThread = threading.Thread(name='Reply-Request-WebServer-Thread-of-Agent-' + str(self.id),
                                                           target=self.replyToRequestFromWebServer,
                                                           kwargs={'myself': self}
                                                           )

            self.annouceThread.setDaemon(True)
            self.readAnnouncementThread.setDaemon(True)
            self.replyToRequestFromWebServerThread.setDaemon(True)

            # Inizio ad ascoltare i messaggi in arrivo sulla mia porta
            self.annouceThread.start()
            self.readAnnouncementThread.start()
            self.replyToRequestFromWebServerThread.start()

    def getIPAddress(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]

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
    """
    def getAvailPowerFromStartingPoint(self, x, other_agent):
        raise NotImplementedError("Questo metodo deve essere implementato da ogni agente che produce potenza")

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
    """
    def waitOptimizationEnd(self):
        raise NotImplementedError("Questo metodo deve essere implementato da ogni agente che non può essere ottimizzato")

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
    Il messaggio contiene il proprio indirizzo IP, la porta utilizzata per ricevere i messaggi di DPOP,
    se l'agente produce energia e se è ottimizzabile:
        (id, host, port, isProducingPower, optimizableAgent)
    """
    def announceMyselfInTheNetwork(self, myself):
        pdata = pickle.dumps((myself.id, myself.host, myself.port, myself.isProducingPower, myself.optimizableAgent))
        sock  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        while (True):
            myself.debug("Annuncio agente {} - {}".format(myself.id, myself.host))
            sock.sendto(pdata, (myself.broadcast_addr, myself.broadcast_port) )
            time.sleep(2)

        sock.close()

    def getOtherAgentsAnnouncement(self, myself):
        listening_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        #listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        listening_socket.bind( ('', myself.broadcast_port) )

        while (True):
            data, addr = listening_socket.recvfrom(65536)
            udata = pickle.loads(data)
            #print(udata)

            agent_id            = udata[0]
            agent_addr          = udata[1]
            agent_port          = udata[2]
            agent_prod_power    = udata[3]
            agent_optimizable   = udata[4]

            if agent_id != myself.id:
                if agent_id not in myself.otherAgents:
                    myself.debug("Ricevuti dati da: {} - {}".format(agent_id, agent_addr))

                    # Se trovo un agente con ID minore del mio, sicuramente io non sono root
                    if agent_id < myself.id:
                        myself.isRoot = False

                    # Imposto il valore del rootID come il minore fra tutti gli agenti considerati
                    self.rootID = min(self.rootID, agent_id)

                    # Aggiungo il nuovo agente
                    self.addNewDiscoveredAgent(agent_id, agent_addr, agent_port,
                                               isProducingPower = agent_prod_power,
                                               optimizableAgent = agent_optimizable)
                # Se l'agente è già presente nella mia lista, aggiorno il fatto che sia ancora vivo
                else:
                    self.otherAgents[agent_id].timeOfDiscovery = time.time()


        listening_socket.close()

    def removeOldDiscoveredAgent(self):
        removed = False

        for index in range(0, len(list(self.otherAgents.keys()))):
            keys = list(self.otherAgents.keys())
            id = keys[index]
            a = self.otherAgents[id]
            if abs(time.time() - a.timeOfDiscovery) > 10:
                self.debug("Rimuovo {}".format(id))
                del self.otherAgents[id]
                removed = True
                break

        if not removed:
            return False

        # Re-imposto la root
        self.isRoot = True
        self.rootID = self.id
        for id in self.otherAgents:
            if id < self.id:
                self.isRoot = False
            self.rootID = min(self.rootID, id)

        return True


    def addNewDiscoveredAgent(self, id, addr, port, isProducingPower = False, optimizableAgent = True):
        discovered = DiscoveredAgent(id, addr, port)
        discovered.isProducingPower = isProducingPower
        discovered.optimizableAgent = optimizableAgent

        self.otherAgents[ id ] = discovered

    def replyToRequestFromWebServer(self, myself):
        web_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        web_sock.bind(('', myself.broadcast_web_port))
        web_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        while (True):
            #data, addr = web_sock.recvfrom(65536)
            #print(addr)
            #print(data)

            data = self.packDataForWebServer()

            web_sock.sendto(json.dumps(data).encode(), (myself.broadcast_addr, myself.broadcast_web_port))
            self.debug("Mando info per il web server")
            time.sleep(2)

        web_sock.close()

    def readAgentConfigurationFromWebServer(self):
        content_folder = os.path.join("/", "var", "www", "html", "api")
        conf_file = os.path.join(content_folder, "conf.json")

        try:
            with open(conf_file) as data_file:
                self.jsonConfiguration = json.load(data_file)
        except FileNotFoundError:
            self.debug("Impossibile trovare il file di configurazione web")
            self.jsonConfiguration = None
        except json.JSONDecodeError:
            self.debug("Errore JSON nella lettura del file di configurazione web")
            self.jsonConfiguration = None

    def writeOnFileConfigurationForWebServer(self, possible_conf):
        content_folder = os.path.join("/", "var", "www", "html", "api")
        poss_conf_file = os.path.join(content_folder, "possible_conf.json")

        with open(poss_conf_file, 'w') as outfile:
            json.dump(possible_conf, outfile)

    """
    Invia i messaggi tramite il protocollo TCP/IP:
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

            # Performance
            self.messages_sent_total_size += sys.getsizeof(pdata)
            self.messages_sent_number     += 1
        except:
            time.sleep(0.1)
            sock.close()
            self.sendMsg(dest_node_id, type, data)
        finally:
            sock.close()

    def listenToMessages(self):
        if self.isListening:
            return True

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

        msg_sender  = udata[0]
        msg_type    = udata[1]
        msg_value   = udata[2]

        # self.debug("[RICEZIONE] ({}, {}): {}".format(int(msg_sender), str(msg_type), msg_value))
        self.msgs[(int(msg_sender), str(msg_type))] = message.Message(msg_type, msg_sender, msg_value)

        # self.debug( self.msgs )

    def printPerformace(self):
        # Prestazioni relative alla dimensione ed al numero di messaggi inviati
        performace_string = "PERFORMANCE:"

        performace_string += "\n\tMessages sent total size: {}".format(self.messages_sent_total_size)
        performace_string += "\n\tMessages sent number: {}".format(self.messages_sent_number)

        self.debug(performace_string)

    def computeFinalCycle(self):
        # Calcolo il mio ciclo e lo invio sulla rete
        start_timestep = self.value
        cycle = self.getVarsFromStartingPoint(start_timestep)['vars']

        # Salvo il file csv
        self.saveFinalCycle(cycle)

        # Invio sulla rete a tutti gli agenti il mio ciclo
        for id in self.otherAgents:
            a = self.otherAgents[id]
            if not a.optimizableAgent:
                self.sendMsg(id, message.MessageType.FINAL_CYCLE, cycle)

    def saveFinalCycle(self, cycle):
        dir = os.path.dirname(__file__)
        output_folder = os.path.join(dir, "output")
        filename_path = os.path.join(output_folder, '{}_{}_cycle.csv'.format(self.name, self.id))

        np.savetxt(filename_path, np.array( cycle ), fmt='%.2f', delimiter=',')

    def debug(self, text):
        print("[{} {}]: {}".format(self.name, self.id, text))

    def start(self):
        if len( self.otherAgents ) == 0:
            self.debug("Sono l'unico agente sulla rete, non posso ottimizzare nulla.")
            return False

        self.killStartThread = False

        # Rimuovo tutti gli agenti che non vengono annunciato da alcuni secondi
        while self.removeOldDiscoveredAgent():
            pass

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

        if self.killStartThread:
            return False

        # Resetto il contenuto del dict messaggi
        self.msgs = {}

        # Avvio la procedura di propagazione dei messaggi di UTIL
        UTILMessagePropagation.start( self )
        if self.killStartThread:
            return False

        # Solamente gli agenti NON root devono attendere il messaggio di VALUE dal loro genitore
        if not self.isRoot:
            VALUEMessagePropagation.start( self )

        if self.killStartThread:
            return False

        # Alla fine dell'intera procedura calcolo il mio ciclo finale
        self.computeFinalCycle()

        if self.killStartThread:
            return False

        if not self.optimizableAgent:
            self.waitOptimizationEnd()
            if self.killStartThread:
                return False

        self.printPerformace()

        return True