from typing import Tuple, List, Any, Dict, Literal, Optional
from enum import Enum
from domain.value_objects import FiringSolution, Point2D, BulletStatus
from domain.models.launcher import Launcher
from domain.rules import normalize_azimuth_angle

from application.ports.launcher_input_port import LauncherInputPort
from application.ports.launcher_output_port import LauncherCommandPort
from application.ports.ui_firing_output_port import FiringStatusOutputPort
from application.dto.angle.packet import AnglePacket
from application.dto import OptoelectronicsState, HardwareEventId
from application.services.target_position_service import TargetPositionService
from application.services.correction_application_service import CorrectionApplicationService


class FiringControlService:
    """Lớp điều khiển hoạt động giàn phóng, tính toán phần tử bắn, gửi lệnh điều khiển ra phần cứng"""
    def __init__(self, 
                 input_port: LauncherInputPort, 
                 output_port: LauncherCommandPort, 
                 targeting_system: TargetPositionService,
                #  correction_service: CorrectionApplicationService=None,
                 launchers: Dict[str, Launcher]=None, 
                 firing_status_observer: FiringStatusOutputPort=None):
        """Khởi tạo dịch vụ điều khiển toàn bộ giàn phóng.
        
        Args:
            input_port (LauncherInputPort): Cổng nhận tín hiệu từ phần cứng.
            output_port (LauncherCommandPort): Cổng gửi lệnh điều khiển.
            targeting_system (TargetPositionService): Hệ thống ngắm mục tiêu.
            launchers (Dict[str, Launcher]): Dictionary map ID -> Giàn phóng.
            firing_status_observer (FiringStatusOutputPort): Cổng báo trạng thái bắn cho UI.
        """
        if launchers is None:
            self.launchers = {'left': Launcher(), 'right': Launcher()}
        else:
            self.launchers = launchers
        self.input_port = input_port
        self.output_port = output_port
        self.targeting_system = targeting_system
        self.firing_status_observer = firing_status_observer
        # self.correction_service = correction_service
        self.optoelectronics_state = OptoelectronicsState()
        
    def on_hardware_event(self, event_id: HardwareEventId, data: Any) -> None:
        """
        Entry point duy nhất cho mọi tín hiệu từ infrastructure
        """
        # print("on hardware event")
        # print(data)
        # print(event_id)
        handler_mapping = {
            HardwareEventId.AMMO_STATUS_LEFT: lambda: self._handle_bullet_status("left", data),
            HardwareEventId.AMMO_STATUS_RIGHT: lambda: self._handle_bullet_status("right", data),
            HardwareEventId.ANGLE_LEFT: lambda: self._handle_current_angle_feedback("left", data),
            HardwareEventId.ANGLE_RIGHT: lambda: self._handle_current_angle_feedback("right", data),
            HardwareEventId.DISTANCE: lambda: self._handle_distance_feedback(data),
            HardwareEventId.AZIMUTH: lambda: self._handle_optoelectronic_azimuth_feedback(data),
        }

        handler = handler_mapping.get(event_id)
        if handler:
            handler()

    def _handle_bullet_status(self, launcher_id: str, bullets_status: List[bool]) -> None:
        """Xử lý tín hiệu báo đạn từ phần cứng

        Args:
            launcher_id (int): id của giàn phóng trong application
            bullets_status (List[bool]): [True/False] * 18, trạng thái của tất cả đạn trong giàn

        Raises:
            ValueError: Số lượng đạn không khớp với số lượng giàn
        """
        launcher = self.launchers[launcher_id]
        # print("[serivce handle bullet status]")
        if len(bullets_status) != launcher.num_ammo:
            raise ValueError("Số lượng đạn không khớp với số lượng giàn")

        for index, status in enumerate(bullets_status):
            index += 1
            if status == False:
                launcher.set_bullet_status(index, BulletStatus.EMPTY)
            elif launcher.get_bullet_status(index) == BulletStatus.EMPTY:
                launcher.set_bullet_status(index, BulletStatus.LOADED)

        if self.firing_status_observer:
            self.firing_status_observer.on_bullet_status_changed(launcher_id, launcher.bullets_statuses)
        
    def _handle_current_angle_feedback(self, launcher_id: str, packet: AnglePacket) -> None:
        launcher = self.launchers[launcher_id]

        azimuth = normalize_azimuth_angle(packet.azimuth)
        elevation = packet.elevation

        launcher.set_current_angle(azimuth, elevation)
        self.firing_status_observer.on_current_angle_changed(launcher_id, packet)

    def compute_all_firing_solutions(self, distance_m: float, use_high_table: bool = False) -> Dict[str, FiringSolution]:
        """Tính phần tử bắn cho tất cả giàn theo cự ly.
        
        Args:
            distance_m (float): cự ly tính bằng mét.
            use_high_table (bool): có sử dụng bảng bắn cao không.
            
        Returns: Dict[str, FiringSolution]
        """
        target_point = self.targeting_system.calculate_target_position(
            distance_m,
            self.optoelectronics_state.azimuth.current_value,  # hoặc lấy từ optoelectronic state
        )

        firing_solutions = self.targeting_system.calculate_firing_solutions(target_point, use_high_table)
        return firing_solutions
    
    def compute_firing_solution(self, launcher_id: str, distance_m: float, use_high_table: bool = False) -> FiringSolution:
        """Lấy phần tử bắn theo ID giàn.
        
        Args:
            launcher_id (str): ID của giàn phóng.
            distance_m (float): cự ly tính bằng mét.
            use_high_table (bool): có sử dụng bảng bắn cao không.
            
        Returns: FiringSolution
        """
        firing_solutions = self.compute_all_firing_solutions(distance_m, use_high_table)
        return firing_solutions[launcher_id]
        
    
    def _handle_distance_feedback(self, distance_m: float) -> None:
        self.optoelectronics_state.distance.current_value = distance_m
        self.firing_status_observer.on_distance_input_changed('left', distance_m)
        self.firing_status_observer.on_distance_input_changed('right', distance_m)
    
    def _handle_optoelectronic_azimuth_feedback(self, azimuth_deg: float) -> None:
        self.optoelectronics_state.azimuth.current_value = azimuth_deg    

    def select_bullets(self, launcher_id: str):
        """Gửi tín hiệu chọn đạn dưới dạng list danh sách id ống phóng cho giàn "launcher_id" ra phần cứng

        Args:
            launcher_id (str): id của giàn phóng trong application
        """
        launcher = self.launchers[launcher_id]
        
        # lấy danh sách đạn được chọn
        choice_bullets = []
        for index in range(1, launcher.num_ammo + 1):  # index là index của danh sách
            if launcher.get_bullet_status(index) == BulletStatus.SELECTED:
                choice_bullets.append(index)
        
        self.output_port.select_bullets(launcher_id, choice_bullets)
        
    def set_target_angle(self, launcher_id: str, azimuth_deg: float, elevation_deg: float, distance_m: float=0):
        """Thiết lập góc tầm góc hướng mục tiêu cho giàn và gửi xuống hardware.
        
        Args:
            launcher_id (str): ID của giàn phóng.
            azimuth_deg (float): góc phương vị tính bằng độ.
            elevation_deg (float): góc tà tính bằng độ.
            distance_m (float): cự ly tính bằng mét.
        """
        launcher = self.launchers[launcher_id]
        launcher.set_target_angle(normalize_azimuth_angle(azimuth_deg), elevation_deg)
        self.output_port.send_target_angle(launcher_id, AnglePacket(normalize_azimuth_angle(azimuth_deg), elevation_deg))
        self.firing_status_observer.on_target_angle_and_distance_changed(launcher_id, AnglePacket(normalize_azimuth_angle(azimuth_deg), elevation_deg), distance_m)
        
    def choose_bullet(self, launcher_id: str, index: int):
        """Chọn đạn số index trên giàn tương ứng và gửi tín hiệu chọn đạn xuống hardware.
        
        Args:
            launcher_id (str): ID của giàn phóng.
            index (int): index của đạn (1 index base).
        """
        launcher = self.launchers[launcher_id]
        launcher.choose_bullet(index)
        if self.firing_status_observer:
            self.firing_status_observer.on_bullet_status_changed(launcher_id, launcher.bullets_statuses)
        self.select_bullets(launcher_id)
        
    def unchoose_bullet(self, launcher_id: str, index: int):
        """Bỏ chọn đạn số index và gửi tín hiệu bỏ chọn đạn xuống hardware.
        
        Args:
            launcher_id (str): ID của giàn phóng.
            index (int): index của đạn (1 index base).
        """
        launcher = self.launchers[launcher_id]
        launcher.unchoose_bullet(index)
        if self.firing_status_observer:
            self.firing_status_observer.on_bullet_status_changed(launcher_id, launcher.bullets_statuses)
        self.select_bullets(launcher_id)
            
    def select_all_bullets(self, launcher_id: Optional[Literal['left', 'right']] = None):
        """Chọn toàn bộ đạn đã nạp trên giàn tương ứng và gửi tín hiệu chọn đạn xuống hardware.
        
        Args:
            launcher_id (Optional[str]): ID của giàn phóng. Nếu không truyền thì chọn toàn bộ đạn trên tất cả các giàn.
        """
        keys = self.launchers.keys()
        if launcher_id:
            keys = [launcher_id]
        for launcher_id in keys:
            launcher = self.launchers[launcher_id]
            for index in range(1, launcher.num_ammo + 1):
                if launcher.get_bullet_status(index) == BulletStatus.LOADED:
                    launcher.choose_bullet(index)

            self.select_bullets(launcher_id)
            if self.firing_status_observer:
                self.firing_status_observer.on_bullet_status_changed(launcher_id, launcher.bullets_statuses)
            
    def unselect_all_bullets(self):
        """Bỏ chọn tất cả đạn đã được chọn ở tất cả các giàn và gửi tín hiệu bỏ chọn đạn xuống hardware."""
        for launcher_id in self.launchers.keys():
            launcher = self.launchers[launcher_id]
            for index in range(1, launcher.num_ammo + 1):
                if launcher.get_bullet_status(index) == BulletStatus.SELECTED:
                    launcher.unchoose_bullet(index)
                    
            self.select_bullets(launcher_id)
            if self.firing_status_observer:
                self.firing_status_observer.on_bullet_status_changed(launcher_id, launcher.bullets_statuses)
      