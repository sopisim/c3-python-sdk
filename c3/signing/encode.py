import base64

from c3.signing.types import CEOpId, CERequest, CERequestOp, OrderData


def encode_order_data(
    order_data: OrderData,
) -> bytearray:
    # Decode and validate account ID
    account = base64.b64decode(order_data.account)
    assert len(account) == 32

    # Encode operation ID
    encoded = bytearray([CEOpId.Settle])

    # Encode account ID
    encoded.extend(account)

    # Encode remaining fields
    encoded.extend(order_data.nonce.to_bytes(8, "big", signed=False))
    encoded.extend(order_data.expires_on.to_bytes(8, "big", signed=False))
    encoded.extend(order_data.sell_slot_id.to_bytes(1, "big", signed=False))
    encoded.extend(order_data.sell_amount.to_bytes(8, "big", signed=False))
    encoded.extend(
        order_data.max_sell_amount_from_pool.to_bytes(8, "big", signed=False)
    )
    encoded.extend(order_data.buy_slot_id.to_bytes(1, "big", signed=False))
    encoded.extend(order_data.buy_amount.to_bytes(8, "big", signed=False))
    encoded.extend(order_data.max_buy_amount_to_pool.to_bytes(8, "big", signed=False))
    return encoded


def encode_user_operation(request: CERequest) -> bytearray:
    match request.op:
        case CERequestOp.Login:
            nonce_as_bytes = request.nonce.encode("ascii")
            return nonce_as_bytes

        case CERequestOp.Borrow | CERequestOp.Lend | CERequestOp.Redeem | CERequestOp.Repay:
            # For borrow and redeem, the amount is negative(taking from the pool)
            amount = (
                -request.amount
                if request.op in (CERequestOp.Borrow, CERequestOp.Redeem)
                else request.amount
            )

            # Encode remaining fields
            result = bytearray([CEOpId.PoolMove, request.slot_id])
            result.extend(amount.to_bytes(8, "big", signed=True))
            return result

        case CERequestOp.Withdraw:
            # Validate receiver address
            # NOTE: This is a bytes field because it is encoded as a string differently on each chain

            # to-do
            # receiverAddress = base64.b64decode(request.receiver.address)

            assert len(request.receiver.address) == 32

            result = bytearray([CEOpId.Withdraw, request.slot_id])
            result.extend(request.amount.to_bytes(8, "big", signed=False))
            result.extend(request.receiver.chain_id.to_bytes(2, "big", signed=False))
            result.extend(request.receiver.address)
            result.extend(request.max_borrow.to_bytes(8, "big", signed=False))
            result.extend(request.max_fees.to_bytes(8, "big", signed=False))
            return result

        case CERequestOp.Delegate:
            result = bytearray([CEOpId.Delegate])
            result.extend(base64.b64decode(request.delegate))
            result.extend(request.creation.to_bytes(8, "big", signed=False))
            result.extend(request.expiration.to_bytes(8, "big", signed=False))
            return result

        case CERequestOp.Liquidate:
            # Validate target address
            target = base64.b64decode(request.target)
            assert len(target) == 32

            # Validate cash is all positive
            if any(amount < 0 for amount in request.cash.values()):
                raise ValueError("Liquidation cash can not be negative")

            # Generate result
            result = bytearray([CEOpId.Liquidate])
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

        case CERequestOp.AccountMove:
            # Validate target address
            target = base64.b64decode(request.target)
            assert len(target) == 32

            # Validate cash and pool are all positive
            if any(amount < 0 for amount in request.cash.values()):
                raise ValueError("Account move cash can not be negative")

            if any(amount < 0 for amount in request.pool.values()):
                raise ValueError("Account move pool can not be negative")

            # Generate result
            result = bytearray([CEOpId.AccountMove])
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

        case CERequestOp.Cancel:
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
