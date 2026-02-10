from PyQt5.QtCore import QObject, pyqtSignal
from application.dto import ElectricalPointStatus, NodeStatus
from application.ports.system_status import SystemStatusPort


class QtSystemStatusAdapter(SystemStatusPort, QObject):

    node_status = pyqtSignal(object)

    def present_node_status(self, dto: NodeStatus):
        self.node_status.emit(dto)
