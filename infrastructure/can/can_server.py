import threading
from typing import Callable, List, Union
import can
from .bus_manager import CANBusManager


class CANServer:
    """
    Infrastructure-level CAN event dispatcher
    """

    def __init__(self, bus_manager: CANBusManager, timeout: float = 0.05):
        self._bus_manager = bus_manager

        self._running = False
        self._thread: Union[threading.Thread, None] = None

        self._subscribers: List[Callable[[can.Message], None]] = []
        self._lock = threading.Lock()
        self._timeout = timeout

    # ---------- subscription ----------

    def subscribe(self, callback: Callable[[can.Message], None]):
        with self._lock:
            self._subscribers.append(callback)

    # ---------- lifecycle ----------

    def start(self):
        if self._running:
            return

        self._running = True
        bus = self._bus_manager.open()

        def _loop():
            while self._running:
                # print("???")
                msg = bus.recv(timeout=self._timeout)  # blocking wait
                if msg is None:
                    continue
                print(msg.data)
                with self._lock:
                    subscribers = list(self._subscribers)

                for function in subscribers:
                    print(function)
                    function(msg)

        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()


    def send(
        self,
        arbitration_id: int,
        data: bytes,
        is_extended_id: bool = False,
    ) -> None:
        """
        Gửi 1 CAN frame
        """
        bus = self._bus_manager.open()

        msg = can.Message(
            arbitration_id=arbitration_id,
            data=data,
            is_extended_id=is_extended_id,
        )
        
        with self._lock:
            # print("")
            bus.send(msg)
    
    def stop(self):
        self._running = False
        
    