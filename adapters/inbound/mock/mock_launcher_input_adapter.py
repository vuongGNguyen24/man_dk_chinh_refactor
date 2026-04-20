import threading
import random
import time
from typing import Dict, Callable, List, Any

from application.ports.launcher_input_port import LauncherInputPort
from application.dto.angle.packet import AnglePacket
from application.dto import HardwareEventId, LauncherBulletStatus


class MockLauncherInputAdapter(LauncherInputPort):
    """
    Fake Launcher inbound adapter.
    Randomly generates launcher data (distance, azimuth, angles, ammo status).
    """

    def __init__(self, interval: float = 0.5):
        self._subscribers: List[Callable[[HardwareEventId, Any], None]] = []
        self.interval = interval
        self._running = False
        self._thread = None

    def subscribe(self, callback: Callable[[HardwareEventId, Any], None]):
        self._subscribers.append(callback)

    def start(self):
        self._running = True
        print("start can adapter")
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _generate_random_ammo_status(self) -> LauncherBulletStatus:
        # Assuming 18 bools for the first list and 18 for the second as an example
        # The CAN implementation unpacked 8+8+2 = 18 flags for each.
        flags1 = [random.choice([True, False]) for _ in range(18)]
        flags2 = [random.choice([True, False]) for _ in range(18)]
        return LauncherBulletStatus(flags1, flags2)

    def _run_loop(self):
        events = [
            HardwareEventId.AMMO_STATUS_LEFT,
            HardwareEventId.AMMO_STATUS_RIGHT,
            HardwareEventId.ANGLE_LEFT,
            HardwareEventId.ANGLE_RIGHT,
            HardwareEventId.DISTANCE,
            HardwareEventId.AZIMUTH,
        ]

        while self._running:
            # Randomly select an event to trigger
            event_id = random.choice(events)
            # print("event id", event_id)
            if event_id in [HardwareEventId.AMMO_STATUS_LEFT, HardwareEventId.AMMO_STATUS_RIGHT]:
                data = self._generate_random_ammo_status()
            elif event_id in [HardwareEventId.ANGLE_LEFT, HardwareEventId.ANGLE_RIGHT]:
                data = AnglePacket(
                    azimuth=round(random.uniform(-70, 70), 1),
                    elevation=round(random.uniform(10, 65), 1)
                )
            elif event_id == HardwareEventId.DISTANCE:
                data = round(random.uniform(1500, 10000.0), 2)
            elif event_id == HardwareEventId.AZIMUTH:
                data = round(random.uniform(-70.0, 70.0), 1)
            else:
                data = None

            for cb in self._subscribers:
                cb(event_id, data)

            time.sleep(self.interval)
