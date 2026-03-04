import yaml
def load_ip_addresses_from_yaml(yaml_path: str):
    raise NotImplementedError

    with open(yaml_path) as f:
        ip_addresses = yaml.load(f, Loader=yaml.FullLoader)