import asyncio
import os
import time
import unittest

from c3.c3exchange import C3Exchange
from c3.signing.signers import AlgorandMessageSigner
from c3.websocket import WebSocketClient, WebSocketClientEvent


class TestWebSockets(unittest.IsolatedAsyncioTestCase):
    async def test_should_connect_sdk(self):
        base_url = "http://localhost:3000/"
        account_mnemonic = os.environ["TEST_ACCOUNT_MNEMONIC"]
        signer = AlgorandMessageSigner.from_mnemonic(mnemonic_string=account_mnemonic)
        c3_client = C3Exchange(base_url)
        account = c3_client.login(signer)
        print(account)
        client = WebSocketClient(
            base_url, account_id=account["accountId"], jwt_token=account["token"]
        )

        connected = False
        received_mkt_data = False

        @client.on(WebSocketClientEvent.Connect)
        async def connect():
            nonlocal connected
            connected = True
            print("Connected")

        @client.on(WebSocketClientEvent.L1MarketData)
        async def print_mkt_data(data):
            print("Mkt Data", data)
            nonlocal received_mkt_data
            received_mkt_data = True

        client.start()

        retry = 5
        while not connected and retry > 0:
            await asyncio.sleep(1)
            --retry
        self.assertTrue(connected, "Should connect to c3 server")
        await client.subscribe_to_market("ETH-USDC")
        await client.subscribe_to_market("AVAX-USDC")

        retry = 5
        while retry > 0 and not received_mkt_data:
            await asyncio.sleep(1)
            --retry
        self.assertTrue(received_mkt_data, "Should be able to subscribe to mkt data")


if __name__ == "__main__":
    unittest.main()
