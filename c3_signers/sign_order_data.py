from abc import ABC, abstractmethod
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
