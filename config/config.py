import yaml

def get_config(env="dev"):
    with open(f"config/{env}.yaml", "r") as f:
        return yaml.safe_load(f)