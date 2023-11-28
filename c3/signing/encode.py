import base64

from algosdk import abi

from c3.signing.types import (
    RequestOperation,
    SignatureRequest,
    SignatureRequestOperationId,
)

ORDER_ABI_FORMAT = "(byte,byte[32],uint64,uint64,byte,uint64,uint64,byte,uint64,uint64)"
HEADER_ABI_FORMAT = "(byte[32],byte[32],uint64)"


def encode_abi_value(value, encoding) -> bytes:
    return abi.ABIType.from_string(encoding).encode(value)


def encode_user_operation_base(request: SignatureRequest) -> bytearray:
    match request.op:
        case RequestOperation.Login:
            nonce_as_bytes = request.nonce.encode("ascii")

            return nonce_as_bytes

        case RequestOperation.Order:
            # Decode and validate account ID
            account = base64.b64decode(request.account)
            assert len(account) == 32

            orderABIvalue = [
                6,
                account,
                request.nonce,
                request.expires_on,
                request.sell_slot_id,
                request.sell_amount,
                request.max_sell_amount_from_pool,
                request.buy_slot_id,
                request.buy_amount,
                request.max_buy_amount_to_pool,
            ]

            return encode_abi_value(value=orderABIvalue, encoding=ORDER_ABI_FORMAT)

        case RequestOperation.Borrow | RequestOperation.Lend | RequestOperation.Redeem | RequestOperation.Repay:
            # For borrow and redeem, the amount is negative(taking from the pool)
            amount = (
                -request.amount
                if request.op in (RequestOperation.Borrow, RequestOperation.Redeem)
                else request.amount
            )

            # Encode remaining fields
            result = bytearray([SignatureRequestOperationId.PoolMove, request.slot_id])
            result.extend(amount.to_bytes(8, "big", signed=True))
            return result

        case RequestOperation.Withdraw:
            # Validate receiver address
            # NOTE: This is a bytes field because it is encoded as a string differently on each chain

            # to-do
            # receiverAddress = base64.b64decode(request.receiver.address)

            assert len(request.receiver.address) == 32

            result = bytearray([SignatureRequestOperationId.Withdraw, request.slot_id])
            result.extend(request.amount.to_bytes(8, "big", signed=False))
            result.extend(request.receiver.chain_id.to_bytes(2, "big", signed=False))
            result.extend(request.receiver.address)
            result.extend(request.max_borrow.to_bytes(8, "big", signed=False))
            result.extend(request.max_fees.to_bytes(8, "big", signed=False))
            return result

        case RequestOperation.Delegate:
            result = bytearray([SignatureRequestOperationId.Delegate])
            result.extend(base64.b64decode(request.delegate))
            result.extend(request.creation.to_bytes(8, "big", signed=False))
            result.extend(request.expiration.to_bytes(8, "big", signed=False))
            return result

        case RequestOperation.Liquidate:
            # Validate target address
            target = base64.b64decode(request.target)
            assert len(target) == 32

            # Validate cash is all positive
            if any(amount < 0 for amount in request.cash.values()):
                raise ValueError("Liquidation cash can not be negative")

            # Generate result
            result = bytearray([SignatureRequestOperationId.Liquidate])
            result.extend(target)

            # Encode headers for cash and pool
            cash_start = (
                1 + len(target) + 2 + 2
            )  # NOTE: 1(op id) + 32(target) + 2(cash count) + 2(pool count)
            result.extend(cash_start.to_bytes(2, "big", signed=False))
            pool_start = cash_start + 2 + len(request.cash) * 9
            result.extend(pool_start.to_bytes(2, "big", signed=False))

            # Encode cash
            result.extend(len(request.cash).to_bytes(2, "big", signed=False))
            for instrument_id in request.cash:
                result.extend(instrument_id.to_bytes(1, "big", signed=False))
                result.extend(
                    request.cash[instrument_id].to_bytes(8, "big", signed=False)
                )

            # Encode pool
            result.extend(len(request.pool).to_bytes(2, "big", signed=False))
            for instrument_id in request.pool:
                result.extend(instrument_id.to_bytes(1, "big", signed=False))
                result.extend(
                    request.pool[instrument_id].to_bytes(8, "big", signed=True)
                )

            return result

        case RequestOperation.AccountMove:
            # Validate target address
            target = base64.b64decode(request.target)
            assert len(target) == 32

            # Validate cash and pool are all positive
            if any(amount < 0 for amount in request.cash.values()):
                raise ValueError("Account move cash can not be negative")

            if any(amount < 0 for amount in request.pool.values()):
                raise ValueError("Account move pool can not be negative")

            # Generate result
            result = bytearray([SignatureRequestOperationId.AccountMove])
            result.extend(target)

            # Encode headers for cash and pool
            cash_start = (
                1 + len(target) + 2 + 2
            )  # NOTE: 1(op id) + 32(target) + 2(cash count) + 2(pool count)
            result.extend(cash_start.to_bytes(2, "big", signed=False))
            pool_start = cash_start + 2 + len(request.cash) * 9
            result.extend(pool_start.to_bytes(2, "big", signed=False))

            # Encode cash
            result.extend(len(request.cash).to_bytes(2, "big", signed=False))
            for instrument_id in request.cash:
                result.extend(instrument_id.to_bytes(1, "big", signed=False))
                result.extend(
                    request.cash[instrument_id].to_bytes(8, "big", signed=False)
                )

            # Encode pool
            result.extend(len(request.pool).to_bytes(2, "big", signed=False))
            for instrument_id in request.pool:
                result.extend(instrument_id.to_bytes(1, "big", signed=False))
                result.extend(
                    request.pool[instrument_id].to_bytes(8, "big", signed=False)
                )
            return result

        case RequestOperation.Cancel:
            # If 'orders' is present, decode each base64 string and concatenate them.
            encoded_orders = b"".join(
                base64.b64decode(order) for order in request.orders
            )

            # If 'allOrdersUntil' is present, decode the base64 string.
            encoded_all_orders_until = (
                base64.b64decode(str(request.all_orders_until).encode())
                if request.all_orders_until
                else b""
            )

            # Concatenate 'encodedOrders' and 'encodedAllOrdersUntil'.
            return b"".join([encoded_orders, encoded_all_orders_until])
        case _:
            raise ValueError(f"Unsupported operation: {request.op}")


def encode_user_operation(request: SignatureRequest) -> bytearray:
    encoded_operation = encode_user_operation_base(request)

    match request.op:
        case RequestOperation.Login | RequestOperation.Cancel:
            # FIXME: Does this need to be base64 encoded?
            # If not, we should probably change it on the server side
            # for consistency.
            return encoded_operation
        case _:
            headerABIvalue = [
                base64.b64decode(request.account),
                request.lease,
                request.last_valid,
            ]

            encodedHeaderABIvalue = encode_abi_value(
                value=headerABIvalue, encoding=HEADER_ABI_FORMAT
            )

            result = bytearray()
            result.extend(b"(C3.IO)0")
            result.extend(encodedHeaderABIvalue)
            result.extend(encoded_operation)

            return base64.b64encode(result)
