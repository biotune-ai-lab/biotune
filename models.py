from typing import Dict

import yaml


def load_model_config() -> Dict:
    """Load all model configurations from models.yaml"""
    try:
        with open("models.yaml", "r") as f:
            config = yaml.safe_load(f)
        return config["models"]
    except FileNotFoundError:
        raise ValueError("Models config not found")
    except KeyError:
        raise ValueError("Invalid config - missing 'models' section")


def get_prompt(model: str, prompt_type: str, **kwargs) -> str:
    """Generic prompt loader for any model type"""
    model_config = load_model_config()

    if model not in model_config:
        raise ValueError(f"Unknown model: {model}")

    if "prompts" not in model_config[model]:
        raise ValueError(f"No prompts configured for model {model}")

    if prompt_type not in model_config[model]["prompts"]:
        raise ValueError(f"No prompt '{prompt_type}' found for model {model}")

    prompt_path = model_config[model]["prompts"][prompt_type]

    try:
        with open(prompt_path) as f:
            template = f.read()
        return template.format(**kwargs) if kwargs else template
    except FileNotFoundError:
        raise ValueError(f"Prompt file not found: {prompt_path}")
    except KeyError as e:
        raise ValueError(f"Missing required parameter in prompt: {e}")


def get_domain_model(function_name: str) -> str:
    """Map function name to corresponding domain model"""
    model_config = load_model_config()

    for model, config in model_config.items():
        if "prompts" in config and function_name in config["prompts"]:
            return model

    raise ValueError(f"No domain model found for function: {function_name}")
