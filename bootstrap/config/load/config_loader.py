import yaml
from typing import Dict
from infrastructure.serial import SerialConfig

class ConfigLoader:
    def __init__(self, config_path: str="bootstrap/config/communication.yaml"):
        self.config_path = config_path
        with open(self.config_path) as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)
    def load_rs485_config(self) -> SerialConfig:
        return SerialConfig.from_dict(self.config['rs485'])
    
    def load_udp_config(self) -> Dict:
        """Trả về cấu hình udp

        Returns:
            Dict: cấu hình udp với cấu trúc: {"host": str, "port": int}
            - host: các địa chỉ mà server có thể nhận được request
            - port: port mà server có thể nhận được request
        """
        return self.config['udp']
    
    def load_can_config(self) -> Dict:
        """Trả về cấu hình CAN

        Returns:
            Dict: cấu hình CAN với cấu trúc: {"channel": str, "bitrate": int}
            - channel: các địa chỉ mà server có thể nhận được request
            - bitrate: port mà server có thể nhận được request
        """
        return self.config['can']
    
    
#legacy code
def load_rs485_config(config_path: str) -> SerialConfig:
    with open(config_path) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        return SerialConfig.from_dict(config['rs485'])