from algosdk import mnemonic

from c3.c3exchange import C3Exchange
from c3.signing.signers import AlgorandMessageSigner, EVMMessageSigner
from c3.utils.constants import TestnetConstants

MNEMONIC = ""
private_key = mnemonic.to_master_derivation_key(MNEMONIC)
signerAlgorand = AlgorandMessageSigner(private_key)

c3Client = C3Exchange(base_url=TestnetConstants.API_URL)
algorandAccount = c3Client.login(signer=signerAlgorand)

orderParams = {
    "marketId": "ETH-USDC",
    "type": "limit",
    "side": "buy",
    "amount": "0.1",
    "price": "1028.33",
}

orderResponse = algorandAccount.submitOrder(orderParams)
