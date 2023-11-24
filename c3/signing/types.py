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

class SignatureMethod(IntEnum):
    ED25519 = 0
    ECDSA = 1


@dataclass
class XChainAddress:
    chain_id: ChainId
    address: bytes  # NOTE: 32-byte address, not base64 encoded because each chain has its own bespoke address format


@dataclass
class SignatureRequest:
    pass


@dataclass
class SignatureRequestSingleAsset(SignatureRequest):
    slot_id: SlotId
    amount: ContractAmount


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
    target: AccountId
    pool: Dict[SlotId, ContractAmount]
    cash: Dict[SlotId, ContractAmount]


@dataclass
class DelegateSignatureRequest(SignatureRequest):
    op: RequestOperation.Delegate
    delegate: AccountId
    creation: Timestamp
    expiration: Timestamp


@dataclass
class AccountMoveSignatureRequest(SignatureRequest):
    op: RequestOperation.AccountMove
    target: AccountId
    pool: Dict[SlotId, ContractAmount]
    cash: Dict[SlotId, ContractAmount]


@dataclass
class CancelSignatureRequest(SignatureRequest):
    op: RequestOperation.Cancel
    user: AccountId
    creator: Address
    orders: list[OrderId] = field(default_factory=list)  # array of orderIds
    all_orders_until: Timestamp = None


@dataclass
class LoginSignatureRequest(SignatureRequest):
    op: RequestOperation.Login
    nonce: str
