from typing import Callable, Any
from application.dto import HardwareEventId
from application.ports.launcher_input_port import LauncherInputPort
from adapters.inbound.can.launcher_input_adapter import CANLauncherInputAdapter
from adapters.inbound.udp.launcher_input_adapter import UDPLauncherInputAdapter

class LauncherInputAdapter(LauncherInputPort):
    """
    Lớp kết hợp CANLauncherInputAdapter và UDPLauncherInputAdapter nhận đồng thời 2 loại tín hiệu.
    Là Inbound Adapter, lớp này chỉ chịu trách nhiệm lắng nghe dữ liệu từ phần cứng (qua CAN và UDP)
    và đẩy vào Application thông qua callback (subscribe).
    """
    def __init__(self, can_adapter: CANLauncherInputAdapter, udp_adapter: UDPLauncherInputAdapter):
        self.can_adapter = can_adapter
        self.udp_adapter = udp_adapter

    def subscribe(self, callback: Callable[[HardwareEventId, Any], None]):
        """
        Đăng ký callback cho cả luồng nhận CAN và UDP.
        Bất cứ khi nào 1 trong 2 kênh nhận được dữ liệu, nó sẽ gọi callback này để đẩy vào App.
        """
        self.can_adapter.subscribe(callback)
        self.udp_adapter.subscribe(callback)

    def start(self):
        """
        Khởi động các tác vụ lắng nghe ngầm nếu có.
        """
        if hasattr(self.can_adapter, 'start'):
            self.can_adapter.start()
        if hasattr(self.udp_adapter, 'start'):
            self.udp_adapter.start()