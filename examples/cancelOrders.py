from c3.c3exchange import C3Exchange
from c3.signing.signers import EVMMessageSigner
from c3.utils.constants import TestnetConstants

c3Client = C3Exchange(base_url=TestnetConstants.API_URL)
signerEVM = EVMMessageSigner("private_key")
ethAccount = c3Client.login(signer=signerEVM)

cancelResponse = ethAccount.cancelMarketOrders(marketId="AVAX-USDC")
