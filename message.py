class MessageType():
    NEIGHBORS   = 'neighbors'   # Contiene i vicini del nodo che lo invia
    PTINFO      = 'ptinfo'      # Informazioni sullo pseudotree: parents, pseudo_parents, children, pseudo_children
    DOMAIN      = 'domain'      # Contiene il dominio del nodo che lo invia
    VARS        = 'vars'        # Contiene tutti i possibili assegnamenti delle varibaili per ogni starting point
    UTIL        = 'util'        # E' il messaggio di UTIL inviato dai figli ai loro genitori e pseudo genitori
    VALUE       = 'value'       # E' il messaggio che contiene il valore assegnato alla variabile controllata
    SP_CONSIDERED_AGENT = 'sp_considered_agent' # ID degli agenti già considerati nel pannello solare

class Message():
    def __init__(self, type, sender, value):
        self.type   = type
        self.sender = sender
        self.value  = value

