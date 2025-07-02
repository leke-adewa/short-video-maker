import os
import google.genai as genai
from agent.logger import ProjectLogger

class ApiKeyManager:
    """
    Manages a pool of Google Gemini API keys, rotating them when one is exhausted.
    """
    def __init__(self, logger: ProjectLogger):
        self.logger = logger
        keys_str = os.getenv("GOOGLE_API_KEYS")
        if not keys_str:
            raise ValueError("GOOGLE_API_KEYS not found in .env file. Please provide a comma-separated list of keys.")

        self.keys = [key.strip() for key in keys_str.split(',')]
        if not self.keys:
            raise ValueError("GOOGLE_API_KEYS is empty.")

        self.current_key_index = 0
        self.client = None
        self._create_client()

    def _create_client(self):
        """Creates and configures a genai.Client with the current API key."""
        if self.current_key_index >= len(self.keys):
            raise Exception("All available API keys have been exhausted.")

        api_key = self.keys[self.current_key_index]
        # Note: The genai library might print a warning if multiple key-related
        # environment variables are set. This is expected behavior.
        os.environ["GOOGLE_API_KEY"] = api_key

        self.client = genai.Client(http_options={'api_version': 'v1alpha'})
        key_identifier = f"Key {self.current_key_index + 1}/{len(self.keys)} (...{api_key[-4:]})"
        self.logger.info(f"API Client initialized with {key_identifier}")

    def get_client(self) -> genai.Client:
        """Returns the current, active client."""
        return self.client

    def switch_key(self):
        """Switches to the next API key in the pool."""
        self.logger.warning(f"Switching from API key {self.current_key_index + 1} due to rate limit.")
        self.current_key_index += 1
        self._create_client() 
