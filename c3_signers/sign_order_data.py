from abc import ABC, abstractmethod
import base64
from dataclasses import dataclass
from typing import Final


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
	def signMessage(message: bytes) -> bytes:
		pass


ORDER_OPERATION: Final[int] = 6


def sign_order_data(
	order_data: OrderData,
	signer: MessageSigner,
) -> SettlementTicket:
	pass

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
