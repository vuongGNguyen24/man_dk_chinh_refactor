import yaml 
from typing import Dict


def from_yaml(yaml_path: str) -> Dict[str, str]:
    """
    Get firing table paths from YAML
    Args:
        yaml_mapping (str): yaml file path

    Returns:
        Dict[str, str]: {"low_table": str, "high_table": str, "slope_correction_table": str}
        - lơw_table: path to CSV file with low firing table
        - high_table: path to CSV file with high firing table
        - slope_correction_table: path to CSV file with slope correction table
    """
    
    config = {}
    with open(yaml_path) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        
    return config