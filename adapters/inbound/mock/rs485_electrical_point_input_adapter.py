import threading
import random
import time
from typing import Dict, Callable, List

from application.ports.electrical_circuit import ElectricalPointInputPort


class MockRS485ElectricalPointInputAdapter(ElectricalPointInputPort):
    """
    Fake RS485 inbound adapter.
    Randomly toggles electrical points.
    """

    def __init__(
        self,
        decode_mapping_choice: Dict[int, Dict[int, str]],
        interval: float = 0.3,
    ):
        self.subscribers: List[Callable[[Dict[str, bool]], None]] = []
        self.decode_mapping_choice = decode_mapping_choice
        self.interval = interval
        self._running = False
        self._thread = None

        self._all_points = self._collect_point_ids()

    def subscribe(self, callback: Callable[[Dict[str, bool]], None]):
        self.subscribers.append(callback)

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
            # random flip 1-2 điểm
            for _ in range(random.randint(1, 2)):
                point = random.choice(self._all_points)
                state[point] = not state[point]

            snapshot = state.copy()

            for cb in self.subscribers:
                cb(snapshot)

            time.sleep(self.interval)