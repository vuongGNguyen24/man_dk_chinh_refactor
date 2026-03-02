import threading
import random
import time
from typing import Dict, Callable, List, Tuple

from application.ports.electrical_circuit import ElectricalPointInputPort


class MockUDPElectricalPointInputAdapter(ElectricalPointInputPort):
    """
    Fake UDP inbound adapter.
    Randomly generates electrical point snapshots.
    """

    def __init__(
        self,
        decode_mapping_choice: Dict[Tuple[str, int], Dict[int, str]],
        interval: float = 0.5,
        debug: bool = False,
    ):
        self._subscribers: List[Callable[[Dict[str, bool]], None]] = []
        self.decode_mapping_choice = decode_mapping_choice
        self.interval = interval
        self._running = False
        self._thread = None
        self._debug = debug
        # flatten tất cả point_id từ mapping
        self._all_points = self._collect_point_ids()

    def subscribe(self, callback: Callable[[Dict[str, bool]], None]):
        self._subscribers.append(callback)

    # -----------------------------------------

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    # -----------------------------------------

    def _collect_point_ids(self) -> List[str]:
        result = []
        for mapping in self.decode_mapping_choice.values():
            result.extend(mapping.values())
        return list(set(result))

    def _run_loop(self):
        state: Dict[str, bool] = {p: False for p in self._all_points}

        while self._running:
            if self._debug:
                print("Mock RS485 snapshot")
                print(state)
            # random flip 1-3 điểm
            for _ in range(random.randint(1, 3)):
                point = random.choice(self._all_points)
                state[point] = not state[point]

            snapshot = state.copy()

            for cb in self._subscribers:
                cb(snapshot)

            time.sleep(self.interval)