import yaml


def _load_model_config():
    """Load model configurations from models.yaml"""
    try:
        with open("models.yaml", "r") as f:
            config = yaml.safe_load(f)
        return config["models"]
    except FileNotFoundError:
        raise ValueError("Models config not found")
    except KeyError:
        raise ValueError("Invalid config - missing 'models' section")


def get_prompt(model: str, prompt_name: str, **kwargs) -> str:
    """Get prompt for specific model and format it with parameters.

    Args:
        model: The model to get the prompt for (e.g., "gpt-4o", "conch")
        prompt_name: Name of the prompt to get (e.g., "system", "subtype_image")
    """
    model_config = _load_model_config()

    if model not in model_config:
        raise ValueError(f"Unknown model: {model}")

    if "prompts" not in model_config[model]:
        raise ValueError(f"No prompts configured for model {model}")

    if prompt_name not in model_config[model]["prompts"]:
        raise ValueError(f"No prompt '{prompt_name}' found for model {model}")

    prompt_path = model_config[model]["prompts"][prompt_name]

    try:
        with open(prompt_path) as f:
            template = f.read()
        return template.format(**kwargs)
    except FileNotFoundError:
        raise ValueError(f"Prompt file not found: {prompt_path}")
    except KeyError as e:
        raise ValueError(f"Missing required parameter in prompt: {e}")


def get_domain_model(function_name: str) -> str:
    """Get the appropriate domain model based on function name."""
    model_config = _load_model_config()  # Changed from load_model_config

    # Search through models to find which one has this function
    for model, config in model_config.items():
        if "prompts" in config and function_name in config["prompts"]:
            return model

    raise ValueError(f"No model found for function: {function_name}")
