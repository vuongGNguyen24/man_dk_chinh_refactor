from typing import Tuple, List

from domain.value_objects import FiringSolution, Point2D, BulletStatus
from domain.models.launcher import Launcher
from domain.ports.launcher_input_port import LauncherInputPort
from domain.ports.launcher_output_port import LauncherCommandPort
from domain.services.targeting_system import TargetingSystem
from domain.rules import normalize_azimuth_angle

class FiringControlService:
    """Lớp hệ thống điều khiển băn tổng quát cho nhiều giàn
    """
    def __init__(self, launchers: Tuple[Launcher], input_port: LauncherInputPort, output_port: LauncherCommandPort, targeting_system: TargetingSystem):
        self.launchers = launchers
        self.input_port = input_port
        self.output_port = output_port
        self.targeting_system = targeting_system
        
    def select_bullets(self, launcher_id: str, bullets: List[int]):
        self.output_port.select_bullets(launcher_id, bullets)
        
    def set_target_azimuth(self, launcher_id: str, angle_deg: float):
        self.output_port.set_target_azimuth(launcher_id, angle_deg)
        
    def set_target_elevation(self, launcher_id: str, angle_deg: float):
        self.output_port.set_target_elevation(launcher_id, angle_deg)
    
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
        
    def compute_firing_solution(self, target_distance: float):
        target_point = self.targeting_system.calculate_target_position(target_distance, self.azimuth_optoelectronic.current_value)
        
        firing_solutions = self.targeting_system.calculate_firing_solutions(target_point)
        
        for index, solution in enumerate(firing_solutions):
            self.launchers[index].set_target_angle(normalize_azimuth_angle(solution.azimuth), solution.elevation)
            
    
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
    
    def set_direct_firing_angle(
        self,
        launcher_id: str,
        elevation_deg: float,
        azimuth_deg: float,
    ):
        azimuth = normalize_azimuth_angle(azimuth_deg)

        launcher = self.launchers[launcher_id]
        launcher.set_target_angle(azimuth, elevation_deg)

        # Gửi lệnh ra phần cứng
        self.output_port.set_target_elevation(launcher_id, elevation_deg)
        self.output_port.set_target_azimuth(launcher_id, azimuth)
        
    def launch_all_ready(self, launcher_id: str):
        launcher = self.launchers[launcher_id]
        ready = launcher.get_ready_bullets()

        if not ready:
            return False

        self.output_port.fire(launcher_id, ready)
        launcher.mark_bullets_fired(ready)
        return True


    


        
        