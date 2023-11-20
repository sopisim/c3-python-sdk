from dataclasses import dataclass

MAINNET_API_URL = "https://api.test.c3.io/v1/instruments"
TESTNET_API_URL = "https://api.c3.io/v1/instruments"
LOCAL_API_URL = "http://localhost:3001"


@dataclass(frozen=True)
class Constants:
    API_URL: str


class MainnetConstants(Constants):
    API_URL = "https://api.c3.io/"


class TestnetConstants(Constants):
    API_URL = "https://api.test.c3.io/"


class LocalHostConstants(Constants):
    API_URL = "http://localhost:3000"
