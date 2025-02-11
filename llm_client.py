from typing import Any, Dict, List, Optional

from openai import OpenAI

import models
from config import Config


class LLMClient:
    """Handles LLM-specific operations"""

    def __init__(self, config: Config):
        self.config = config
        self.model = config.LLM_MODEL
        self.model_config = models.load_model_config()

        # Initialize client based on model
        if config.LLM_MODEL == "gpt-4o":
            self.client = OpenAI(api_key=config.LLM_API_KEY)
        else:
            self.client = OpenAI(
                base_url="https://api.studio.nebius.ai/v1/", api_key=config.LLM_API_KEY
            )

    def _get_model_params(
        self, override_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get model parameters with optional overrides"""
        # Start with empty dict
        params = {}

        # Get model config and parameters if they exist and are not None
        model_config = self.model_config.get(self.model, {})
        if (
            model_config
            and "parameters" in model_config
            and model_config["parameters"] is not None
        ):
            params = model_config["parameters"].copy()

        # Add any override parameters
        if override_params:
            params.update(override_params)

        return params

    def _parse_response(self, response: Any) -> str:
        """Parse response based on model type"""
        content = response.choices[0].message.content
        if self.model == "gpt-4o":
            return content
        else:  # Add DeepSeek or Llava-specific parsing if needed
            # Remove the thinking section enclosed in <think> tags
            import re

            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)
            # Remove userStyle tags
            content = re.sub(r"<userStyle>.*?</userStyle>", "", content)
            # Remove random backslashes before underscores
            content = content.replace("\_", "_")
            # Clean up any extra whitespace
            content = content.strip()
            return content

    def get_completion(
        self,
        messages: List[Dict[str, str]],
        override_params: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Get completion from the LLM"""
        params = self._get_model_params(override_params)

        response = self.client.chat.completions.create(
            model=self.model, messages=messages, **params
        )

        return self._parse_response(response)
