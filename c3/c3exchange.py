from typing import Any, Dict

from c3.account import Account
from c3.api import ApiClient
from c3.signing.encode import encode_user_operation
from c3.signing.signers import AlgorandMessageSigner, EVMMessageSigner, MessageSigner
from c3.signing.types import LoginSignatureRequest, RequestOperation
from c3.utils.constants import Constants, MainnetConstants, get_constants


class C3Exchange(ApiClient):
    def __init__(
        self,
        base_url: str = MainnetConstants.API_URL,
        constants: Constants = None,
        instrumentsInfo: Dict[str, Any] = None,
        marketsInfo: Dict[str, Any] = None,
    ):
        self.base_url = base_url
        super().__init__(base_url)

        self.Constants = constants if constants is not None else get_constants(base_url)
        self.instrumentsInfo = (
            instrumentsInfo if instrumentsInfo is not None else self._getInstruments()
        )
        self.marketsInfo = (
            marketsInfo if marketsInfo is not None else self._getMarkets()
        )

    def login(self, signer: MessageSigner, chainId: int = None) -> Account:
        """Auth to C3 Exchange

        Args:
            signer (MessageSigner): eth_account or algosdk account
            chainId (int, optional): Womrhole chain id.

        Returns:
            Account: C3 Account Client
        """
        if isinstance(signer, AlgorandMessageSigner):
            chainId = self.Constants.ALGORAND_CHAIN_ID
        elif isinstance(signer, EVMMessageSigner):
            chainId = self.Constants.ETH_CHAIN_ID

        address = signer.address()

        loginStartResponse = self.get(
            "v1/login/start", {"chainId": chainId, "address": address}
        )
        nonce = loginStartResponse["nonce"]

        loginData = LoginSignatureRequest(op=RequestOperation.Login, nonce=nonce)
        loginDataEncoded = encode_user_operation(loginData)
        signature = signer.sign_message(loginDataEncoded)

        loginCompleteResponse = self.post(
            "v1/login/complete",
            {"chainId": chainId, "address": address, "signature": signature},
        )

        return Account(
            signer=signer,
            accountId=loginCompleteResponse["accountId"],
            apiToken=loginCompleteResponse["token"],
            instrumentsInfo=self.instrumentsInfo,
            marketsInfo=self.marketsInfo,
            base_url=self.base_url,
            constants=self.Constants,
        )

    def _getInstruments(self) -> Dict[str, Any]:
        instrumentsResponse = self.get("v1/instruments")
        instrumentsDict = {
            item["id"]: {
                **{k: v for k, v in item.items() if k != "id"},
                **{"slotId": index},
            }
            for index, item in enumerate(instrumentsResponse)
        }

        return instrumentsDict

    def _getMarkets(self) -> Dict[str, Any]:
        marketsResponse = self.get("v1/markets")
        marketsDict = {
            item["id"]: {k: v for k, v in item.items() if k != "id"}
            for item in marketsResponse
        }

        return marketsDict
