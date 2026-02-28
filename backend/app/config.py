import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    amadeus_api_key: str = os.getenv("AMADEUS_API_KEY", "")
    amadeus_api_secret: str = os.getenv("AMADEUS_API_SECRET", "")
    amadeus_env: str = os.getenv("AMADEUS_ENV", "test")  # test or production

    @property
    def amadeus_base_url(self) -> str:
        if self.amadeus_env == "production":
            return "https://api.amadeus.com"
        return "https://test.api.amadeus.com"

    @property
    def amadeus_enabled(self) -> bool:
        return bool(self.amadeus_api_key and self.amadeus_api_secret)


settings = Settings()
