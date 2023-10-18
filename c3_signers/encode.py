import base64
from dataclasses import dataclass
from enum import Enum, IntEnum, StrEnum
from typing import Dict, Final, List, TypeAlias


@dataclass
class OrderData(object):
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


def encode_order_data(
	order_data: OrderData,
) -> bytearray:
	# Encode operation ID
	encoded = bytearray([CEOpId.Settle])

	# Encode account ID
	account = base64.b64decode(order_data.account)
	assert len(account) == 32
	encoded.extend(account)

	# Encode remaining fields
	encoded.extend(order_data.nonce.to_bytes(8, 'big', signed=False))
	encoded.extend(order_data.expiresOn.to_bytes(8, 'big', signed=False))
	encoded.extend(order_data.sellSlotId.to_bytes(1, 'big', signed=False))
	encoded.extend(order_data.sellAmount.to_bytes(8, 'big', signed=False))
	encoded.extend(order_data.maxSellAmountFromPool.to_bytes(8, 'big', signed=False))
	encoded.extend(order_data.buySlotId.to_bytes(1, 'big', signed=False))
	encoded.extend(order_data.buyAmount.to_bytes(8, 'big', signed=False))
	encoded.extend(order_data.maxBuyAmountToPool.to_bytes(8, 'big', signed=False))
	
	# Return
	return encoded


class CERequestOp(StrEnum):
	Deposit = 'deposit'
	Withdraw = 'withdraw'
	Lend = 'lend'
	Redeem = 'redeem'
	Borrow = 'borrow'
	Repay = 'repay'
	Liquidate = 'liquidate'
	Delegate = 'delegate'
	AccountMove = 'account-move'


class CEOpId(IntEnum):
	Deposit = 0
	Withdraw = 1
	PoolMove = 2
	Delegate = 3
	Liquidate = 4
	AccountMove = 5
	Settle = 6


AccountId: TypeAlias = str # NOTE: This is an account ID without the C3_ prefix
SlotId: TypeAlias = int # NOTE: Unsigned 8 bit number
ChainId: TypeAlias = int # NOTE: Wormhole chain ID https://docs.wormhole.com/wormhole/reference/constants
ContractAmount: TypeAlias = int # NOTE: Unsigned 64 bit number
Timestamp: TypeAlias = int # NOTE: Unix timestamp in seconds


class XChainAddress(object):
	chain_id: ChainId
	address: bytes # NOTE: 32-byte address, not base64 encoded because each chain has its own bespoke address format


class CERequest(object):
	pass


class CESingleAssetRequest(CERequest):
	slot_id: SlotId
	amount: ContractAmount


class CEWithdrawRequest(CESingleAssetRequest):
	op: CERequestOp.Withdraw
	receiver: XChainAddress
	maxBorrow: ContractAmount
	maxFees: ContractAmount


class CELendRequest(CESingleAssetRequest):
	op: CERequestOp.Lend


class CERedeemRequest(CESingleAssetRequest):
	op: CERequestOp.Redeem


class CEBorrowRequest(CESingleAssetRequest):
	op: CERequestOp.Borrow


class CERepayRequest(CESingleAssetRequest):
	op: CERequestOp.Repay


class CELiquidateRequest(CERequest):
	op: CERequestOp.Liquidate
	target: AccountId
	pool: Dict[SlotId, ContractAmount]
	cash: Dict[SlotId, ContractAmount]


class CEDelegateRequest(CERequest):
	op: CERequestOp.Delegate
	delegate: AccountId
	creation: Timestamp
	expiration: Timestamp


class CEAccountMoveRequest(CERequest):
	op: CERequestOp.AccountMove
	target: AccountId
	pool: Dict[SlotId, ContractAmount]
	cash: Dict[SlotId, ContractAmount]


def encode_user_operation(request: CERequest) -> bytearray:
	match request.op:
		case CERequestOp.Borrow | CERequestOp.Lend | CERequestOp.Redeem | CERequestOp.Repay:
			amount = -request.amount if request.op in (CERequestOp.Borrow, CERequestOp.Redeem) else request.amount

			result = bytearray([CEOpId.PoolMove, request.slot_id])
			result.extend(amount.to_bytes(8, 'big', signed=True))
			return result

		case CERequestOp.Withdraw:
			assert len(request.receiver.address) == 32

			max_borrow = request.maxBorrow or 0
			max_fees = request.maxFees

			result = bytearray([CEOpId.Withdraw, request.slot_id])
			result.extend(request.amount.to_bytes(8, 'big', signed=False))
			result.extend(request.receiver.chainId.to_bytes(2, 'big', signed=False))
			result.extend(request.receiver.address)
			result.extend(max_borrow.to_bytes(8, 'big', signed=False))
			result.extend(max_fees.to_bytes(8, 'big', signed=False))
			return result
			
		case CERequestOp.Delegate:
			result = bytearray([CEOpId.Delegate])
			result.extend(base64.b64decode(request.delegate))
			result.extend(request.creation.to_bytes(8, 'big', signed=False))
			result.extend(request.expiration.to_bytes(8, 'big', signed=False))
			return result

		case CERequestOp.Liquidate:
			target = base64.b64decode(request.target)
			assert len(target) == 32

			if any(amount < 0 for amount in request.cash.values()):
				raise ValueError('Liquidation cash can not be negative')

			result = bytearray([CEOpId.Liquidate])
			result.extend(target)
			for instrument_id in request.cash:
				result.extend(instrument_id.to_bytes(1, 'big', signed=False))
				result.extend(request.cash[instrument_id].to_bytes(8, 'big', signed=False))
			for instrument_id in request.pool:
				result.extend(instrument_id.to_bytes(1, 'big', signed=False))
				result.extend(request.pool[instrument_id].to_bytes(8, 'big', signed=True))
			return result

		case CERequestOp.AccountMove:
			target = base64.b64decode(request.target)
			assert len(target) == 32

			if any(amount < 0 for amount in request.cash.values()):
				raise ValueError('Account move cash can not be negative')

			if any(amount < 0 for amount in request.pool.values()):
				raise ValueError('Account move pool can not be negative')

			result = bytearray([CEOpId.AccountMove])
			result.extend(target)
			for instrument_id in request.cash:
				result.extend(instrument_id.to_bytes(1, 'big', signed=False))
				result.extend(request.cash[instrument_id].to_bytes(8, 'big', signed=False))
			for instrument_id in request.pool:
				result.extend(instrument_id.to_bytes(1, 'big', signed=False))
				result.extend(request.pool[instrument_id].to_bytes(8, 'big', signed=False))
			return result
