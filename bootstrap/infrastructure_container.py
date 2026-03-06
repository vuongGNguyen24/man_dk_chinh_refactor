from infrastructure.udp import UDPSocketManager, UDPServer
from infrastructure.can.can_server import CANServer
from infrastructure.can.bus_manager import CANBusManager
from bootstrap.config import ConfigLoader

class InfrastructureContainer:

    def __init__(self, config: ConfigLoader):
        self.config = config

        self.udp_server = None
        self.can_server = None

    def build(self):
        udp_config = self.config.load_udp_config()
        self.udp_server = UDPServer(
            UDPSocketManager(
                udp_config["host"],
                udp_config["port"],
            )
        )

        can_config = self.config.load_can_config()
        self.can_server = CANServer(CANBusManager(can_config["channel"], can_config["bitrate"]))

    def start(self):
        if self.udp_server:
            self.udp_server.start()

        # if self.can_server:
        #     self.can_server.start()

