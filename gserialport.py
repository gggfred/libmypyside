import logging

from PySide2.QtCore import QUuid, Signal, QByteArray
from PySide2.QtSerialPort import QSerialPort, QSerialPortInfo

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.WARNING)
logger = logging.getLogger('GSerialPort')  # Logger for this module
logger.setLevel(logging.DEBUG)  # Debugging for this file. # (2)

class GSerialPort(QSerialPort):
    dataReceived = Signal(QByteArray)

    def __init__(self):
        super(GSerialPort, self).__init__()
        self._uid = QUuid.createUuid().toString()

        self.readyRead.connect(self.onPortReadyRead)

    def pDebug(self, msg):
        logger.debug("{}: {}".format(self.name(),msg))

    def pInfo(self, msg):
        logger.info("{}: {}".format(self.name(),msg))

    def name(self):
        return self.portName() + " " + self._uid

    def getPorts(self):
        return QSerialPortInfo.availablePorts()

    def onPortReadyRead(self):
        if self.canReadLine() == False:
            return

        data = self.readLine()

        logData = "RX: {}".format(data)
        self.pDebug(logData)

        self.dataReceived.emit(data)

    def send(self, data):
        if self.isOpen() == False:
            logData = "TX: PORT CLOSED"
            self.pDebug(logData)
            return

        logData = "TX: {}".format(data)

        try:
            self.write(data)
        except:
            logData = "TX: ERROR AL ENVIAR"
        finally:
            self.pDebug(logData)
