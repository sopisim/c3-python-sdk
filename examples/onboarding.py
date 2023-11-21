import base64

from c3.c3exchange import C3Exchange
from c3.signing.signers import AlgorandMessageSigner
from c3.utils.constants import TestnetConstants

signer = AlgorandMessageSigner(base64.b64encode(bytes(range(32))))

c3Client = C3Exchange(base_url=TestnetConstants.API_URL)

account = c3Client.login(signer=signer)
