from typing import Tuple, List, Any, Dict

from domain.value_objects import FiringSolution, Point2D, BulletStatus
from domain.models.launcher import Launcher
# from domain.services.targeting_system import TargetingSystem
from domain.rules import normalize_azimuth_angle

from application.ports.launcher_input_port import LauncherInputPort
from application.ports.launcher_output_port import LauncherCommandPort
from application.ports.ui_firing_output_port import FiringStatusOutputPort
from application.dto.angle.packet import AnglePacket
from application.dto.optoelectronics_state import OptoelectronicsState
from application.services.target_position_service import TargetPositionService
class FiringControlService:
    """Lớp hệ thống điều khiển băn tổng quát cho nhiều giàn
    """
    def __init__(self, 
                 launchers: Dict[str, Launcher], 
                 input_port: LauncherInputPort, 
                 output_port: LauncherCommandPort, 
                 targeting_system: TargetPositionService,
                 bullet_observer: FiringStatusOutputPort=None):
        self.launchers = launchers
        self.input_port = input_port
        self.output_port = output_port
        self.targeting_system = targeting_system
        self.optoelectronics_state = OptoelectronicsState()
        self.bullet_observer = bullet_observer
        self.input_port.subcribe(self._on_hardware_event)
        
    
        
    # def set_target_elevation(self, launcher_id: str, angle_deg: float):
    #     self.output_port.set_target_elevation(launcher_id, angle_deg)
    def _on_hardware_event(self, can_id: int, data: Any) -> None:
        """
        Entry point duy nhất cho mọi tín hiệu từ CAN
        """

        if can_id in (0x98, 0x99):  # AMMO_STATUS_LEFT / RIGHT
            self._handle_bullet_status(can_id, data)

        elif can_id in (0x00F, 0x00E):  # ANGLE_CANNON_LEFT / RIGHT
            self._handle_current_angle_feedback(can_id, data)

        elif can_id == 0x100:  # DISTANCE
            self._handle_distance_feedback(data)
        
        elif can_id == 0x102:  # AZIMUTH
            self._handle_optoelectronic_azimuth_feedback(data)

    def _handle_bullet_status(self, launcher_id: int, bullets_status: List[bool]) -> None:
        """Xử lý tín hiệu báo đạn từ phần cứng

        Args:
            launcher_id (int): id của giàn phóng trong application
            bullets_status (List[bool]): [True/False] * 18, trạng thái của tất cả đạn trong giàn

        Raises:
            ValueError: Số lượng đạn không khớp với số lượng giàn
        """
        launcher = self.launchers[launcher_id]

        if len(bullets_status) != launcher.num_ammo:
            raise ValueError("Số lượng đạn không khớp với số lượng giàn")

        for index, status in enumerate(bullets_status):
            if status == BulletStatus.EMPTY:
                launcher.set_bullet_status(index, BulletStatus.EMPTY)
            elif launcher.get_bullet_status(index) == BulletStatus.EMPTY:
                launcher.set_bullet_status(index, status)
        
        if self.bullet_observer:
            self.bullet_observer.on_bullet_status_changed(launcher_id, bullets_status)
        
    def _handle_current_angle_feedback(self, launcher_id: int, packet: AnglePacket) -> None:
        launcher = self.launchers[launcher_id]

        azimuth = normalize_azimuth_angle(packet.azimuth)
        elevation = packet.elevation

        launcher.set_current_angle(azimuth, elevation)

    def compute_all_firing_solutions(self, distance_m: float, use_high_table: bool = False) -> Dict[str, FiringSolution]:
        target_point = self.targeting_system.calculate_target_position(
            distance_m,
            self.optoelectronics_state.azimuth.current_value,  # hoặc lấy từ optoelectronic state
        )

        firing_solutions = self.targeting_system.calculate_firing_solutions(target_point)
        return firing_solutions
    
    def compute_firing_solution(self, launcher_id: str, distance_m: float, use_high_table: bool = False) -> FiringSolution:
        firing_solutions = self.compute_all_firing_solutions(distance_m, use_high_table)
        return firing_solutions[launcher_id]
        
    
    def _handle_distance_feedback(self, distance_m: float) -> None:
        self.optoelectronics_state.distance.current_value = distance_m
        self.set_target_angle()
    
    def _handle_optoelectronic_azimuth_feedback(self, azimuth_deg: float) -> None:
        self.optoelectronics_state.azimuth.current_value = azimuth_deg
    
    def update_bullet_status(self):
        """Cập nhật trạng thái đạn từ dữ liệu phần cứng

        Raises:
            ValueError: Nếu số lượng đạn không khớp với số lượng giàn
        """
        id_launcher, bullets_status = self.input_port.on_ammo_status()
        if len(bullets_status) != len(self.launchers[id_launcher]):
            raise ValueError("Số lượng đạn không khớp với số lượng giàn")
        
        # Ưu tiên tín hiệu phần cứng
        for index, status in enumerate(bullets_status):
            if status == BulletStatus.EMPTY:
                self.launchers[id_launcher].set_bullet_status(index, BulletStatus.EMPTY)
            elif self.launchers[id_launcher].get_bullet_status(index) == BulletStatus.EMPTY:
                self.launchers[id_launcher].set_bullet_status(index, status)
     
               
    def update_launcher_position(self):
        """
        Cập nhật góc tầm và góc hướng của một giàn phóng qua tín hiệu phần cứng
        """
        
        id_launcher, elevation_deg, azimuth_deg = self.input_port.on_angle_feedback()
        self.launchers[id_launcher].set_target_angle(normalize_azimuth_angle(azimuth_deg), elevation_deg)
        
            
    def select_bullets(self, launcher_id: str):
        """Gửi tín hiệu chọn đạn cho giàn "launcher_id" ra phần cứng

        Args:
            launcher_id (str): id của giàn phóng trong application
        """
        launcher = self.launchers[launcher_id]
        
        # lấy danh sách đạn được chọn
        choice_bullets = []
        for index in range(1, launcher.num_ammo + 1):
            if launcher.get_bullet_status(index) == BulletStatus.SELECTED:
                choice_bullets.append(index)
        
        self.output_port.select_bullets(launcher_id, choice_bullets)
        
    def set_target_angle(self, launcher_id: str, azimuth_deg: float, elevation_deg: float):
        
        launcher = self.launchers[launcher_id]
        launcher.set_target_angle(normalize_azimuth_angle(azimuth_deg), elevation_deg)
        self.output_port.send_target_angle(launcher_id, AnglePacket(normalize_azimuth_angle(azimuth_deg), elevation_deg))
    
    def set_target_distance(
        self,
        launcher_id: str,
        distance_m: float,
        azimuth_deg: float,
        use_high_table: bool = False,
    ):
        self._use_high_table[launcher_id] = use_high_table

        target_point = self.targeting_system.calculate_target_position(
            distance_m,
            azimuth_deg,
        )

        solution: FiringSolution = self.targeting_system.calculate_single_solution(
            launcher_id,
            target_point,
            use_high_table=use_high_table,
        )

        azimuth = normalize_azimuth_angle(solution.azimuth)

        launcher = self.launchers[launcher_id]
        launcher.set_target_angle(azimuth, solution.elevation)

        self.output_port.set_target_elevation(launcher_id, solution.elevation)
        self.output_port.set_target_azimuth(launcher_id, azimuth)

        return solution
    
        
    # def launch_all_ready(self, launcher_id: str):
    #     launcher = self.launchers[launcher_id]
    #     ready = launcher.get_ready_bullets()

    #     if not ready:
    #         return False

    #     self.output_port.fire(launcher_id, ready)
    #     launcher.mark_bullets_fired(ready)
    #     return True


    


        
        