import json

from c3.c3exchange import C3Exchange
from c3.signing.signers import EVMMessageSigner
from c3.utils.constants import MainnetConstants, TestnetConstants

signerEVM = EVMMessageSigner("PK")

c3Client = C3Exchange(base_url=TestnetConstants.API_URL)


ethAccount = c3Client.login(
    signer=signerEVM,
    primaryAccountId="C3_AAAAAAAAAAAAAAAAAAA_EXAMPLE",
    primaryAccountAddress="0xEXAMPLE",
)

print(ethAccount.address)
print(ethAccount.accountId)
primaryAccountBalance = ethAccount.getBalance()


print(json.dumps(primaryAccountBalance, indent=4))
