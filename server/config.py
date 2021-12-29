import yaml


class GetCfg():
    @classmethod
    def get_id_tag(cls, path="../../config.yaml"):
        with open(path, 'r') as f:
            cfg = yaml.safe_load(f)
            return cfg['chargePoint']['id_tag']