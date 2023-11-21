from dataclasses import dataclass
from typing import Type


@dataclass(frozen=True)
class Constants:
    API_URL: str
    ALGORAND_CHAIN_ID: int
    AVAX_CHAIN_ID: int
    ETH_CHAIN_ID: int


class MainnetConstants(Constants):
    API_URL = "https://api.c3.io/"
    ALGORAND_CHAIN_ID = 8
    AVAX_CHAIN_ID = 6
    ETH_CHAIN_ID = 2


class TestnetConstants(Constants):
    API_URL = "https://api.test.c3.io/"
    ALGORAND_CHAIN_ID = 8
    AVAX_CHAIN_ID = 6
    ETH_CHAIN_ID = 2


class LocalHostConstants(Constants):
    API_URL = "http://localhost:3000"
    ALGORAND_CHAIN_ID = 8
    AVAX_CHAIN_ID = 6
    ETH_CHAIN_ID = 2


constants_mapping = {
    "https://api.c3.io/": MainnetConstants,
    "https://api.test.c3.io/": TestnetConstants,
    "http://localhost:3000": LocalHostConstants,
}


def get_constants(base_url: str, enviroment: str = None) -> Type[Constants]:
    constants_class = None
    if base_url:
        constants_class = constants_mapping.get(base_url)
    elif enviroment:
        constants_class = constants_mapping.get(enviroment)

    if constants_class:
        return constants_class  # Return the constants_class
    else:
        raise ValueError(f"No constants defined for URL: {base_url}")
