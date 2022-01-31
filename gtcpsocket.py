import logging
from os import close

from PySide2.QtCore import QByteArray, QObject, Signal, Slot, QTimer
from PySide2.QtNetwork import QTcpSocket, QHostAddress, QAbstractSocket

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.WARNING)
logger = logging.getLogger('gclient')  # Logger for this module
logger.setLevel(logging.INFO)  # Debugging for this file. # (2)


class GTcpSocket(QTcpSocket):
    _ip = ""
    _port = 0
    _timer_reconnection = 0
    _reconnect = 0
    _socketState = 0

    dataReceived = Signal(QByteArray)
    connected = Signal()
    disconnected = Signal()

    logout = Signal(str)
    status = Signal(str)

    def __init__(self):
        super(GTcpSocket, self).__init__()

        self._timer_reconnection = QTimer()
        self._timer_reconnection.timeout.connect(self.tryConnect)

        self.stateChanged.connect(self.onSocketStateChanged)
        self.readyRead.connect(self.onSocketReadyRead)

        self._reconnect = False
        self._running = False
        self._socketState = QAbstractSocket.UnconnectedState

    def __del__(self):
        print("bye :(")

    def setIP(self, ip):
        self._ip = ip

    def setPort(self, port):
        self._port = port

    def start(self):
        self._running = True
        self.tryConnect()
        if self._reconnect == True:
            self._timer_reconnection.start(5000)

    def stop(self):
        self._running = False
        super(GTcpSocket, self).close()
        self.close()

    @Slot()
    def tryConnect(self):
        if self._socketState == QAbstractSocket.UnconnectedState:
            self.connectToHost(QHostAddress(self._ip), self._port)

    @Slot(QAbstractSocket.SocketState)
    def onSocketStateChanged(self, state):
        self._socketState = state
        if state == QAbstractSocket.HostLookupState:
            logger.info("%s: Lookup for Host", self.objectName())
        elif state == QAbstractSocket.ConnectingState:
            logger.info("%s: Connecting to Host", self.objectName())
            self.status.emit("Conectando")
        elif state == QAbstractSocket.ConnectedState:
            logger.info("%s: Connected to Host", self.objectName())
            self._timer_reconnection.stop()
            self.status.emit("Conectado")
            self.connected.emit()
        elif state == QAbstractSocket.UnconnectedState:
            logger.info("%s: Disconnected to Host", self.objectName())
            self.status.emit("Desconectado")

            super(GTcpSocket, self).close()
            self.close()

            self._timer_reconnection.stop()
            if self._reconnect and self._running == True:
                self._timer_reconnection.start()

            self.disconnected.emit()
        elif state == QAbstractSocket.BoundState:
            logger.info("%s: BoundState", self.objectName())
        elif state == QAbstractSocket.ListeningState:
            logger.info("%s: ListeningState", self.objectName())
        elif state == QAbstractSocket.ClosingState:
            logger.info("%s: ClosingState", self.objectName())

    @Slot()
    def onSocketReadyRead(self):
        data = self.readAll()

        logData = "RX: %s" % data
        logger.info("%s: %s" % (self.objectName(), logData))
        self.logout.emit(logData)

        self.dataReceived.emit(data)

    @Slot()
    def setReconnect(self, enable):
        self._reconnect = enable

    @Slot(str)
    def send(self, data):
        if self.isOpen() == False:
            logData = "TX: ERROR SOCKET CERRADO"
            logger.info("%s: %s" % (self.objectName(), logData))
            self.logout.emit(logData)
            return

        logData = "TX: %s" % data

        try:
            self.write(data)
        except ValueError as v:
            print(v)
            logData = "TX: ERROR AL ENVIAR"
        except TypeError as e:
            print(e)
            logData = "TX: ERROR AL ENVIAR"
        finally:
            logger.info("%s: %s" % (self.objectName(), logData))
            self.logout.emit(logData)
