class MessageType():
    NEIGHBORS   = 'neighbors'   #Contiene i vicini del nodo che lo invia
    PTINFO      = 'ptinfo'      #Informazioni sullo pseudotree: parents, pseudo_parents, children, pseudo_children
    DOMAIN      = 'domain'      #Contiene il dominio del nodo che lo invia

class Message():
    def __init__(self, type, sender, value):
        self.type   = type
        self.sender = sender
        self.value  = value

