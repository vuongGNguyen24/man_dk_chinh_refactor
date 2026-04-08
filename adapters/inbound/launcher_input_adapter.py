from adapters.inbound.can.launcher_input_adapter import CANLauncherInputAdapter
from adapters.inbound.udp.launcher_input_adapter import UDPLauncherInputAdapter

class LauncherInputAdapter:
    """
    Lớp kết hợp CANLauncherInputAdapter và UDPLauncherInputAdapter nhận đồng thời 2 loại tín hiệu
    """
    def __init__(self, can_adapter: CANLauncherInputAdapter, udp_adapter: UDPLauncherInputAdapter):
        self.can_adapter = can_adapter
        self.udp_adapter = udp_adapter
        