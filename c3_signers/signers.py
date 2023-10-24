from abc import ABC, abstractmethod
from algosdk import util, account
from eth_account import Account, messages

from c3_signers.encode import OrderData, encode_order_data
from c3_signers.types import SettlementTicket


class MessageSigner(ABC):
	@abstractmethod
	def account_id(self) -> str:
		pass

	@abstractmethod
	def public_key(self) -> bytes:
		pass

	@abstractmethod
	def sign_message(self, message: bytes) -> str:
		pass


class AlgorandMessageSigner(MessageSigner):
	def __init__(self, private_key: str) -> None:
		self.private_key = private_key
		super().__init__()

	def account_id(self) -> str:
		return "C3_" + account.address_from_private_key(self.private_key)

	def public_key(self) -> bytes:
		return util.encoding.decode_address(account.address_from_private_key(self.private_key))

	def sign_message(self, message: bytes) -> str:
		return util.sign_bytes(message, self.private_key)


class Web3MessageSigner(MessageSigner):
	def __init__(self, private_key: str) -> None:
		self.private_key = private_key
		super().__init__()

	def account_id(self) -> str:
		# FIXME: is this correct?
		return "C3_" + Account.from_key(self.private_key).address()

	def public_key(self) -> bytes:
		# FIXME: is this correct?
		return Account.from_key(self.private_key).address()

	def sign_message(self, message: bytes) -> str:
		msg = messages.encode_defunct(message)
		return Account.sign_message(msg, private_key=self.private_key)


def sign_order_data(
	order_data: OrderData,
	signer: MessageSigner,
) -> SettlementTicket:
	return SettlementTicket(
		order_data.account,
		order_data.sell_slot_id,
		order_data.buy_slot_id,
		order_data.sell_amount,
		order_data.buy_amount,
		order_data.max_sell_amount_from_pool,
		order_data.max_buy_amount_to_pool,
		order_data.expires_on,
		order_data.nonce,
		signer.public_key(),
		signer.sign_message(encode_order_data(order_data)),
	)
