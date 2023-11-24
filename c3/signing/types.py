from dataclasses import dataclass, field
from enum import IntEnum, StrEnum
from typing import Dict, TypeAlias

AccountId: TypeAlias = (
    str  # NOTE: This is the address in bytes. check decode_address function
)
Address: TypeAlias = str  # NOTE: we3 address
OrderId: TypeAlias = str
SlotId: TypeAlias = int  # NOTE: getInstruments() returns the SlotIds per asset
ChainId: TypeAlias = int  # NOTE: Wormhole chain ID https://docs.wormhole.com/wormhole/reference/constants
ContractAmount: TypeAlias = int  # NOTE: Unsigned 64 bit number
Timestamp: TypeAlias = int  # NOTE: Unix timestamp in seconds
Nonce: TypeAlias = int  # NOTE: Unsigned 64 bit number
Signature: TypeAlias = str  # NOTE: Base64 encoded signature
LeaseValue: TypeAlias = bytes # NOTE: A 32 byte array of random bytes or all zeros for no lease


@dataclass
class OrderData:
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
class RequestOperation(StrEnum):
    Deposit = "deposit"
    Withdraw = "withdraw"
    Lend = "lend"
    Redeem = "redeem"
    Borrow = "borrow"
    Repay = "repay"
    Liquidate = "liquidate"
    Delegate = "delegate"
    AccountMove = "account-move"
    Cancel = "cancel"
    Login = "login"
    Order = "order"


# NOTE: These are internal IDs used by the contract to identify operations
class SignatureRequestOperationId(IntEnum):
    Deposit = 0
    Withdraw = 1
    PoolMove = 2  # NOTE: The RequestOperation Lend/Redeem/Borrow/Repay operations all map to this
    Delegate = 3
    Liquidate = 4
    AccountMove = 5
    Settle = 6  # NOTE: This is a special operation ID used for order creation


@dataclass
class XChainAddress:
    chain_id: ChainId
    address: bytes  # NOTE: 32-byte address, not base64 encoded because each chain has its own bespoke address format


@dataclass
class SignatureRequest:
    op: RequestOperation
    pass


@dataclass
class SignatureRequestSingleAsset(SignatureRequest):
    account: AccountId
    slot_id: SlotId
    amount: ContractAmount
    
    lease: LeaseValue
    last_valid: Timestamp


@dataclass
class WithdrawSignatureRequest(SignatureRequestSingleAsset):
    op: RequestOperation.Withdraw
    receiver: XChainAddress
    max_borrow: ContractAmount
    max_fees: ContractAmount


@dataclass
class LendSignatureRequest(SignatureRequestSingleAsset):
    op: RequestOperation.Lend


@dataclass
class CERedeemRequest(SignatureRequestSingleAsset):
    op: RequestOperation.Redeem


@dataclass
class BorrowSignatureRequest(SignatureRequestSingleAsset):
    op: RequestOperation.Borrow


@dataclass
class RepaySignatureRequest(SignatureRequestSingleAsset):
    op: RequestOperation.Repay


@dataclass
class OrderSignatureRequest(SignatureRequest):
    op: RequestOperation.Order
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
class LiquidateSignatureRequest(SignatureRequest):
    op: RequestOperation.Liquidate
    account: AccountId
    target: AccountId
    pool: Dict[SlotId, ContractAmount]
    cash: Dict[SlotId, ContractAmount]


@dataclass
class DelegateSignatureRequest(SignatureRequest):
    op: RequestOperation.Delegate
    account: AccountId
    delegate: AccountId
    creation: Timestamp
    expiration: Timestamp


@dataclass
class AccountMoveSignatureRequest(SignatureRequest):
    op: RequestOperation.AccountMove
    account: AccountId
    target: AccountId
    pool: Dict[SlotId, ContractAmount]
    cash: Dict[SlotId, ContractAmount]


@dataclass
class CancelSignatureRequest(SignatureRequest):
    op: RequestOperation.Cancel
    orders: list[OrderId] = field(default_factory=list)  # array of orderIds
    all_orders_until: Timestamp = None


@dataclass
class LoginSignatureRequest(SignatureRequest):
    op: RequestOperation.Login
    nonce: str
    # TODO: We should have the account here for consistency
