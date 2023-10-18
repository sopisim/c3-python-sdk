from dataclasses import dataclass
from enum import IntEnum, StrEnum
from typing import Dict, TypeAlias


AccountId: TypeAlias = str # NOTE: This is an account ID without the C3_ prefix
SlotId: TypeAlias = int # NOTE: Unsigned 8 bit number
ChainId: TypeAlias = int # NOTE: Wormhole chain ID https://docs.wormhole.com/wormhole/reference/constants
ContractAmount: TypeAlias = int # NOTE: Unsigned 64 bit number
Timestamp: TypeAlias = int # NOTE: Unix timestamp in seconds
Nonce: TypeAlias = int # NOTE: Unsigned 64 bit number
Signature: TypeAlias = str # NOTE: Base64 encoded signature


@dataclass
class OrderData(object):
	account: AccountId
	sell_slot_id: SlotId
	buy_slot_id: SlotId
	sell_amount: ContractAmount
	buy_amount: ContractAmount
	max_sell_amount_from_pool: ContractAmount
	max_buy_amount_to_pool: ContractAmount
	expires_on: Timestamp
	nonce: Nonce


@dataclass
class SettlementTicket(OrderData):
	creator: AccountId
	signature: Signature


# NOTE: These are the operation names as they appear in the C3 OpenAPI spec
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


# NOTE: These are internal IDs used by the contract to identify operations
class CEOpId(IntEnum):
	Deposit = 0
	Withdraw = 1
	PoolMove = 2 # NOTE: The CERequestOp Lend/Redeem/Borrow/Repay operations all map to this
	Delegate = 3
	Liquidate = 4
	AccountMove = 5
	Settle = 6 # NOTE: This is a special operation ID used for order creation


@dataclass
class XChainAddress(object):
	chain_id: ChainId
	address: bytes # NOTE: 32-byte address, not base64 encoded because each chain has its own bespoke address format


@dataclass
class CERequest(object):
	pass


@dataclass
class CESingleAssetRequest(CERequest):
	slot_id: SlotId
	amount: ContractAmount


@dataclass
class CEWithdrawRequest(CESingleAssetRequest):
	op: CERequestOp.Withdraw
	receiver: XChainAddress
	max_borrow: ContractAmount
	max_fees: ContractAmount


@dataclass
class CELendRequest(CESingleAssetRequest):
	op: CERequestOp.Lend


@dataclass
class CERedeemRequest(CESingleAssetRequest):
	op: CERequestOp.Redeem


@dataclass
class CEBorrowRequest(CESingleAssetRequest):
	op: CERequestOp.Borrow


@dataclass
class CERepayRequest(CESingleAssetRequest):
	op: CERequestOp.Repay


@dataclass
class CELiquidateRequest(CERequest):
	op: CERequestOp.Liquidate
	target: AccountId
	pool: Dict[SlotId, ContractAmount]
	cash: Dict[SlotId, ContractAmount]


@dataclass
class CEDelegateRequest(CERequest):
	op: CERequestOp.Delegate
	delegate: AccountId
	creation: Timestamp
	expiration: Timestamp


@dataclass
class CEAccountMoveRequest(CERequest):
	op: CERequestOp.AccountMove
	target: AccountId
	pool: Dict[SlotId, ContractAmount]
	cash: Dict[SlotId, ContractAmount]
