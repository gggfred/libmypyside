from os import close

from libpr import GTcpSocket
import logging
import random

from PySide2.QtCore import QObject, Signal, Slot
from PySide2.QtNetwork import QHostAddress, QTcpServer

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.WARNING)
logger = logging.getLogger('gtcpserver')  # Logger for this module
logger.setLevel(logging.INFO)  # Debugging for this file. # (2)


class GTcpServer(QTcpServer):
    _port = 0
    _server = 0
    logout = Signal(str)
    status = Signal(str)
    clientConnected = Signal(int)
    connected = Signal(GTcpSocket)

    def __init__(self):
        super(GTcpServer, self).__init__()

    def setPort(self, port):
        self._port = port

    def start(self):
        logger.info("%s: Listening on %s", self.objectName(), self._port)
        self.listen(QHostAddress("0.0.0.0"), self._port)

    def stop(self):
        super(GTcpServer, self).close()
        self.close()

    def incomingConnection(self, handle: int) -> None:
        logger.info("{0} client connected".format(self.objectName()))
        self.clientConnected.emit(handle)
