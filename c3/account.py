import time
from typing import Any, Dict

from c3.api import ApiClient
from c3.signing.encode import encode_user_operation
from c3.signing.signers import MessageSigner
from c3.signing.types import OrderSignatureRequest, RequestOperation
from c3.utils.constants import Constants, MainnetConstants, get_constants
from c3.utils.utils import amountToContract


class Account(ApiClient):
    def __init__(
        self,
        signer: MessageSigner,
        instrumentsInfo: Dict[str, Any],
        marketsInfo: Dict[str, Any],
        accountId: str = None,
        apiToken: str = None,
        base_url: str = MainnetConstants.API_URL,
        constants: Constants = None,
    ):
        super().__init__(base_url)

        self.accountId = accountId
        self.signer = signer
        self.base64address = signer.base64address()
        self.address = signer.address()

        self.base_url = base_url
        self.Constants = constants if constants is not None else get_constants(base_url)

        self.instrumentsInfo = instrumentsInfo
        self.marketsInfo = marketsInfo

        self.lastNonceStored = int(round(time.time() * 1000))

        self.apiToken = apiToken
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.apiToken}",
            }
        )

    def getBalance(self):
        return self.get(f"v1/accounts/{self.accountId}/balance")
