import base64
import binascii
from abc import ABC, abstractmethod

from algosdk import account, mnemonic, util
from eth_account import Account, messages

from c3.signing.encode import encode_user_operation_base
from c3.signing.types import SettlementTicket


# Utility function for base64address
def base64address(address: str) -> bytes:
    """
    Encodes an address into its base64 representation.
    Automatically detects whether it's an Algorand or EVM address.

    Args:
        address (str): The blockchain address to encode.

    Returns:
        bytes: The base64 encoded address.
    """

    def is_ethereum_address(addr: str) -> bool:
        """Checks if the address is an Ethereum address."""
        return (
            addr.startswith("0x") and len(addr) == 42
        )  # Ethereum addresses are 42 characters long including '0x'

    def is_algorand_address(addr: str) -> bool:
        """Checks if the address is an Algorand address."""
        try:
            # Attempt to decode as an Algorand address.
            util.encoding.decode_address(addr)
            return True
        except (ValueError, TypeError, binascii.Error, AttributeError):
            return False

    if is_ethereum_address(address):
        address = address[2:]  # Strip '0x'
        bytes_address = binascii.unhexlify(address)
        bytes_address = (
            bytes(32 - len(bytes_address)) + bytes_address
        )  # Pad for Ethereum

    elif is_algorand_address(address):
        bytes_address = util.encoding.decode_address(address)
    else:
        raise ValueError("Unsupported or unrecognized address type.")

    return base64.b64encode(bytes_address)


class MessageSigner(ABC):
    @abstractmethod
    def address(self) -> str:
        pass

    @abstractmethod
    def sign_message(self, message: bytes) -> str:
        pass

    @abstractmethod
    def base64address(self) -> bytes:
        pass


# to-do receive algo sdk account as init value


class AlgorandMessageSigner(MessageSigner):
    @staticmethod
    def from_mnemonic(mnemonic_string: str):
        pk = mnemonic.to_private_key(mnemonic_string)
        return AlgorandMessageSigner(pk)

    @staticmethod
    def from_master_key(private_key: str):
        pk = mnemonic.from_master_derivation_key(private_key)
        return AlgorandMessageSigner(pk)

    def __init__(self, private_key: str) -> None:
        self.private_key = private_key
        super().__init__()

    def address(self) -> str:
        return account.address_from_private_key(self.private_key)

    def base64address(self) -> bytes:
        """Encodes Algorand address into base64."""
        address = self.address()
        return base64address(address)

    def sign_message(self, message: bytes) -> str:
        return util.sign_bytes(message, self.private_key)


# to-do receive eth_account account as init value
class EVMMessageSigner(MessageSigner):
    """ "
    Ethereum Message Signer

    It is a eth_account account wrapper to sign messages and decode address

    """

    def __init__(self, private_key: str) -> None:
        self.private_key = private_key
        super().__init__()

    def address(self) -> str:
        return Account.from_key(self.private_key).address

    def base64address(self) -> bytes:
        """Encodes Ethereum address into base64."""
        address = self.address()
        return base64address(address)

    def sign_message(self, message: bytes) -> str:
        msg = messages.encode_defunct(message)
        hexBytesSignature = Account.sign_message(
            msg, private_key=self.private_key
        ).signature

        base64_encoded_signature = base64.b64encode(hexBytesSignature).decode("utf-8")

        return base64_encoded_signature
