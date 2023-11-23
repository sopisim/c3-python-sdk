import base64
import json
import time
from decimal import Decimal
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

    # FIX ME
    def submitOrder(self, orderParams: Dict[str, Any]):
        """
        Create an order.

        Args:
            order_params (Dict[str, Any]): A dictionary containing order parameters.

        Returns:
            order.id (str): The order id.
        """

        marketId = orderParams["marketId"]

        baseId = self.marketsInfo[marketId]["baseInstrument"]["id"]
        quoteId = self.marketsInfo[marketId]["quoteInstrument"]["id"]

        baseInstrumentInfo = self.instrumentsInfo[baseId]
        quoteInstrumentInfo = self.instrumentsInfo[quoteId]

        orderData = {
            "type": orderParams["type"],
            "side": orderParams["side"],
            "amount": orderParams["amount"],
            "price": orderParams["price"]
            if orderParams["type"] == "limit" and "price" in orderParams
            else None,
        }

        if orderData["side"] == "buy":
            orderData["max_borrow"] = amountToContract(
                orderParams.get("maxBorrow", "0"), baseInstrumentInfo["asaDecimals"]
            )
            orderData["max_repay"] = amountToContract(
                orderParams.get("maxRepay", "0"), quoteInstrumentInfo["asaDecimals"]
            )
        else:
            orderData["max_borrow"] = amountToContract(
                orderParams.get("maxBorrow", "0"), quoteInstrumentInfo["asaDecimals"]
            )
            orderData["max_repay"] = amountToContract(
                orderParams.get("maxRepay", "0"), baseInstrumentInfo["asaDecimals"]
            )

        def _getBuySellValues(orderData: dict):
            values = {}
            if orderData["type"] == "market":
                values["buyAmount"], values["sellAmount"] = "0", "0"

                if orderData["side"] == "buy":
                    values["buySlotId"], values["sellSlotId"] = (
                        baseInstrumentInfo["slotId"],
                        quoteInstrumentInfo["slotId"],
                    )
                else:
                    values["buySlotId"], values["sellSlotId"] = (
                        quoteInstrumentInfo["slotId"],
                        baseInstrumentInfo["slotId"],
                    )

            # limit orders
            else:
                quoteAmount = Decimal(orderData["amount"]) * Decimal(orderData["price"])

                if orderData["side"] == "buy":
                    values["buyAmount"] = amountToContract(
                        orderData["amount"], baseInstrumentInfo["asaDecimals"]
                    )
                    values["buySlotId"] = baseInstrumentInfo["slotId"]

                    values["sellAmount"] = amountToContract(
                        quoteAmount, quoteInstrumentInfo["asaDecimals"]
                    )
                    values["sellSlotId"] = quoteInstrumentInfo["slotId"]

                else:
                    values["buyAmount"] = amountToContract(
                        quoteAmount, quoteInstrumentInfo["asaDecimals"]
                    )
                    values["buySlotId"] = quoteInstrumentInfo["slotId"]

                    values["sellAmount"] = amountToContract(
                        orderData["amount"], baseInstrumentInfo["asaDecimals"]
                    )
                    values["sellSlotId"] = baseInstrumentInfo["slotId"]

            return values

        values = _getBuySellValues(orderData)

        # to-do
        # validateOrder(orderParams)

        # one day if not specified
        expires_on = orderParams.get("expiresOn", int(time.time()) + 86400)
        client_order_id = orderParams.get("clientOrderId", "")

        orderNonce = self.lastNonceStored
        self.lastNonceStored += 1

        orderDataToSign = OrderSignatureRequest(
            op=RequestOperation.Order,
            account=self.base64address,
            sell_slot_id=values["sellSlotId"],
            buy_slot_id=values["buySlotId"],
            sell_amount=values["sellAmount"],
            buy_amount=values["buyAmount"],
            max_sell_amount_from_pool=orderData["max_repay"],
            max_buy_amount_to_pool=orderData["max_borrow"],
            expires_on=expires_on,
            nonce=orderNonce,
        )

        encoded_order = base64.b64encode(
            encode_user_operation(orderDataToSign)
        ).decode()

        signature = self.signer.sign_message(base64.b64decode(encoded_order))
        print("signature", signature)

        orderData["creator"] = self.address
        orderData["sentTime"] = int(time.time())

        orderPayload = {
            "marketId": marketId,
            "type": orderData["type"],
            "side": orderData["side"],
            "size": orderData["amount"],
            "price": orderData["price"],
            "clientOrderId": client_order_id,
            "sentTime": orderData["sentTime"],
            "settlementTicket": {
                "account": self.base64address.decode("utf-8"),
                "sellSlotId": values["sellSlotId"],
                "buySlotId": values["buySlotId"],
                "sellAmount": str(values["sellAmount"]),
                "buyAmount": str(values["buyAmount"]),
                "maxSellAmountFromPool": "0",
                "maxBuyAmountToPool": "0",
                "expiresOn": expires_on,
                "nonce": orderNonce,
                "creator": self.address,
                "signature": signature,
            },
        }

        orderResponse = self.post(
            f"v1/accounts/{self.accountId}/markets/{marketId}/orders", orderPayload
        )

        return orderResponse
