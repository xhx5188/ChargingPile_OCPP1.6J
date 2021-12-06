import yaml


class GetCfg():
    @classmethod
    def get_id_tag(cls):
        yaml_file = "../../config.yaml"
        with open(yaml_file, 'r') as f:
            cfg = yaml.safe_load(f)
            return cfg['chargePoint']['id_tag']