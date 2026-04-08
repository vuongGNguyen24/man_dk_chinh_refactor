import yaml
from typing import Dict, Set, Tuple


def load_rs485_mapping_from_yaml(yaml_mapping: str) -> Dict[Tuple[int, int], Dict[int, str]]:
    """Khởi tạo mapping từ vị trí bit đến id của điểm điểm cần đo thông điện cho adapter, được gọi khi khởi tạo object

    Args:
        yaml_mapping (str): file yaml có các mapping từ bit đến id của điểm điểm cần đo thông điện cho adapter, ví dụ cấu trúc:
        ban_dk_tu_xa:
            id: 1
            left:
                id: 0x11
                mapping:
                0: '11'
                1: '13'
                2: '15'
            right:
                id: 0x12
                mapping:
                0: '12'
                1: '14'
                2: '15'  
        """
    
    with open(yaml_mapping) as f:
        bit_mask_to_point_id = yaml.load(f, Loader=yaml.FullLoader)
        left_id = bit_mask_to_point_id['ban_dk_tu_xa']['left']['id']
        right_id = bit_mask_to_point_id['ban_dk_tu_xa']['right']['id']
        left_mapping = bit_mask_to_point_id['ban_dk_tu_xa']['left']['mapping']
        right_mapping = bit_mask_to_point_id['ban_dk_tu_xa']['right']['mapping']
        header_id = bit_mask_to_point_id['ban_dk_tu_xa']['id']
        return {
            (header_id, left_id): left_mapping,
            (header_id, right_id): right_mapping,
        }

def load_udp_mapping_from_yaml(yaml_mapping: str, ip_addresses_yaml: str) -> Dict[Tuple[int, str], Dict[int, str]]:
    """Khởi tạo mapping từ vị trí bit đến id của điểm điểm cần đo thông điện cho adapter, được gọi khi khởi tạo object

    Args:
        yaml_mapping (str): file yaml có các mapping từ bit đến id của điểm điểm cần đo thông điện cho adapter, ví dụ cấu trúc:
            bang_dk_tai_cho:
                id: 2
                left_mapping:
                    0: '25'
                    1: '29'
                    3: '31'
                    4: '33'
                    5: '35'
                right_mapping:
                    0: '26'
                    1: '28'
                    3: '30'
                    4: '32'
                    5: '34'
                    
        ip_addresses_yaml str: yaml có các ip của các node, với cấu trúc:
                "ip_jetson_left": "192.168.1.100",
                "ip_jetson_right": "192.168.1.101",
    """
    
    with open(yaml_mapping) as f:
        bit_mask_to_point_id = yaml.load(f, Loader=yaml.FullLoader)
        ip_addresses = None
        with open(ip_addresses_yaml) as f:
            ip_addresses = yaml.load(f, Loader=yaml.FullLoader)
        ID_BANG_DK_TAI_CHO = bit_mask_to_point_id['bang_dk_tai_cho']['id']
        ID_TU_DK_TAI_CHO = bit_mask_to_point_id['tu_dk_tai_cho']['id']
        IP_LEFT = ip_addresses['ip_jetson_left']
        IP_RIGHT = ip_addresses['ip_jetson_right']
        
        return {
            (ID_BANG_DK_TAI_CHO, IP_LEFT): bit_mask_to_point_id['bang_dk_tai_cho']['left_mapping'],
            (ID_BANG_DK_TAI_CHO, IP_RIGHT): bit_mask_to_point_id['bang_dk_tai_cho']['right_mapping'],
            (ID_TU_DK_TAI_CHO, IP_LEFT): bit_mask_to_point_id['tu_dk_tai_cho']['left_mapping'],
            (ID_TU_DK_TAI_CHO, IP_RIGHT): bit_mask_to_point_id['tu_dk_tai_cho']['right_mapping'],
        }
            
            
def load_allow_points_from_yaml(yaml_mapping: str) -> Set[int]:
    """Khởi tạo mapping từ vị trí bit đến id của điểm điểm cần đo thông điện cho adapter, được gọi khi khởi tạo object

    Args:
        yaml_mapping (str): file yaml có các mapping từ bit đến id của điểm điểm cần đo thông điện cho adapter, ví dụ cấu trúc:
            ban_dk_tu_xa:
                id: 1
                mapping:
                    0: '11'
                    1: '12'
                    2: '13'
                    3: '14'
                    4: '15'
                    5: '16'
    """
    result = set()
    with open(yaml_mapping) as f:
        bit_mask_to_point_id = yaml.load(f, Loader=yaml.FullLoader)
        for d in bit_mask_to_point_id.values():
            for k, v in d.items():
                if k.endswith('mapping'):
                    result |= set(v.values())
    return result
            
        