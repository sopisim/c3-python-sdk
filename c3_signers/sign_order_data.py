from abc import ABC, abstractmethod
import base64
from dataclasses import dataclass
from typing import Final
from algosdk import util
from eth_account import Account, messages


@dataclass
class OrderData:
	account: str
	sellSlotId: int
	buySlotId: int
	sellAmount: int
	buyAmount: int
	maxSellAmountFromPool: int
	maxBuyAmountToPool: int
	expiresOn: int
	nonce: int


@dataclass
class SettlementTicket(OrderData):
	creator: str
	signature: str


class MessageSigner(ABC):
	@abstractmethod
	def address() -> str:
		pass

	@abstractmethod
	def signMessage(self, message: bytes) -> str:
		pass


class AlgorandMessageSigner(MessageSigner):
	def __init__(self, private_key: str) -> None:
		self.private_key = private_key
		super().__init__()

	def signMessage(self, message: bytes) -> str:
		return util.sign_bytes(message, self.private_key)


class Web3MessageSigner(MessageSigner):
	def __init__(self, private_key: str) -> None:
		self.private_key = private_key
		super().__init__()

	def signMessage(self, message: bytes) -> str:
		msg = messages.encode_defunct(message)
		return Account.sign_message(msg, private_key=self.private_key)


ORDER_OPERATION: Final[int] = 6


def sign_order_data(
	order_data: OrderData,
	signer: MessageSigner,
) -> SettlementTicket:
	return SettlementTicket(
		order_data.account,
		order_data.sellSlotId,
		order_data.buySlotId,
		order_data.sellAmount,
		order_data.buyAmount,
		order_data.maxSellAmountFromPool,
		order_data.maxBuyAmountToPool,
		order_data.expiresOn,
		order_data.nonce,
		signer.address(),
		signer.signMessage(encode_order_data(order_data)),
	)

def encode_order_data(
	order_data: OrderData,
) -> bytearray:
	# Encode operation ID
	encoded = bytearray([ORDER_OPERATION])

	# Encode account ID
	account = base64.b64decode(order_data.account)
	assert len(account) == 32
	encoded.extend(account)

	# Encode remaining fields
	encoded.extend(order_data.nonce.to_bytes(8, 'big', False))
	encoded.extend(order_data.expiresOn.to_bytes(8, 'big', False))
	encoded.extend(order_data.sellSlotId.to_bytes(1, 'big', False))
	encoded.extend(order_data.sellAmount.to_bytes(8, 'big', False))
	encoded.extend(order_data.maxSellAmountFromPool.to_bytes(8, 'big', False))
	encoded.extend(order_data.buySlotId.to_bytes(1, 'big', False))
	encoded.extend(order_data.buyAmount.to_bytes(8, 'big', False))
	encoded.extend(order_data.maxBuyAmountToPool.to_bytes(8, 'big', False))
	
	# Return
	return encoded
