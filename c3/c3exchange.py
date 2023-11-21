from c3.api import ApiClient
from c3.signing.encode import encode_user_operation
from c3.signing.signers import AlgorandMessageSigner, MessageSigner, Web3MessageSigner
from c3.signing.types import CELoginRequest, CERequestOp
from c3.utils.constants import Constants, MainnetConstants, get_constants

# from c3.account import Account


class C3Exchange(ApiClient):
    def __init__(
        self, base_url: str = MainnetConstants.API_URL, constants: Constants = None
    ):
        self.base_url = base_url
        self.Constants = constants if constants is not None else get_constants(base_url)
        super().__init__(base_url)

    def login(self, signer: MessageSigner, chainId: int = None) -> None:
        """Auth to C3 Exchange

        Args:
            signer (MessageSigner): eth_account or algosdk account
            chainId (int, optional): Womrhole chain id.

        Returns:
            Account: C3 Account Client
        """
        if isinstance(signer, AlgorandMessageSigner):
            chainId = self.Constants.ALGORAND_CHAIN_ID
        elif isinstance(signer, Web3MessageSigner):
            chainId = self.Constants.ETH_CHAIN_ID

        address = signer.address()

        loginStartResponse = self.get(
            "v1/login/start", {"chainId": chainId, "address": address}
        )
        nonce = loginStartResponse["nonce"]

        loginData = CELoginRequest(op=CERequestOp.Login, nonce=nonce)
        loginDataEncoded = encode_user_operation(loginData)
        signature = signer.sign_message(loginDataEncoded)

        loginCompleteResponse = self.post(
            "v1/login/complete",
            {"chainId": chainId, "address": address, "signature": signature},
        )

        return loginCompleteResponse
