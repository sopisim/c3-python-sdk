from c3.c3exchange import C3Exchange
from c3.signing.signers import EVMMessageSigner
from c3.utils.constants import MainnetConstants, TestnetConstants

signerEVM = EVMMessageSigner("PK")

c3Client = C3Exchange(base_url=TestnetConstants.API_URL)


ethAccount = c3Client.login(
    signer=signerEVM,
    primaryAccountId="C3_AAAAA_EXAMPLE",
    primaryAccountAddress="0xEXAMPLE",
)

orderParams = {
    "marketId": "ETH-USDC",
    "type": "limit",
    "side": "sell",
    "amount": "0.1",
    "price": "3028.33",
}

orderResponse = ethAccount.submitOrder(orderParams)

print(orderResponse)
