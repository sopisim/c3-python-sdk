import base64

from algosdk import encoding, mnemonic

from c3.signing.encode import encode_user_operation
from c3.signing.signers import AlgorandMessageSigner
from c3.signing.types import (
    AccountMoveSignatureRequest,
    BorrowSignatureRequest,
    CancelSignatureRequest,
    CERedeemRequest,
    DelegateSignatureRequest,
    LendSignatureRequest,
    LiquidateSignatureRequest,
    LoginSignatureRequest,
    OrderSignatureRequest,
    RepaySignatureRequest,
    RequestOperation,
    WithdrawSignatureRequest,
    XChainAddress,
)

signer = AlgorandMessageSigner(base64.b64encode(bytes(range(32))))
print("Created signer with address " + signer.address())
print()


def test_encode_login():
    login_data = LoginSignatureRequest(
        op=RequestOperation.Login,
        nonce="Welcome to C3:\n\nClick to sign and accept the C3 Terms of Service (https://c3.io/tos)\n\nThis request will not trigger a blockchain transaction or cost any gas fees.\n\nMjY3ODgtMTcwMDQ2MTU1NzY2NC1V77+977+9NGHvv71fFe+/vVt177+9Od6077+9ZVHvv71+77+977+9RWQs77+9be+/ve+/vVhy77+9",
    )

    expected_encoding = b"Welcome to C3:\n\nClick to sign and accept the C3 Terms of Service (https://c3.io/tos)\n\nThis request will not trigger a blockchain transaction or cost any gas fees.\n\nMjY3ODgtMTcwMDQ2MTU1NzY2NC1V77+977+9NGHvv71fFe+/vVt177+9Od6077+9ZVHvv71+77+977+9RWQs77+9be+/ve+/vVhy77+9"
    actual_encoding = encode_user_operation(login_data)

    expected_sig = "J9vmxX1L4aRE4JUpmH1VTLLK4lBOKhOSTXi60vNG+KUh+p2VejTzHI+nK/ENcf5ZwwQ9MFcp+tavpiTvPHXsBw=="
    actual_sig = signer.sign_message(actual_encoding)

    print("CANCEL", login_data)
    print("ENCODED", bytearray(actual_encoding))
    print("SIGNATURE", actual_sig)
    print()

    assert actual_encoding == expected_encoding
    assert expected_sig == actual_sig


def test_encode_order_data():
    # ORDER DATA {
    #   account: 'AOQQPP7TZYIL4HLQ3UMOOS6ATFT6JVRQTOSQ2XY53SDGIESVGG4MPFYUMQ',
    #   sellSlotId: 42,
    #   buySlotId: 23,
    #   sellAmount: 10000000n,
    #   buyAmount: 10000000n,
    #   maxBuyAmountToPool: 10000000n,
    #   maxSellAmountFromPool: 10000000n,
    #   expiresOn: 1234,
    #   nonce: 1234
    # }
    # ENCODED BgOhB7/zzhC+HXDdGOdLwJln5NYwm6UNXx3chmQSVTG4AAAAAAAABNIAAAAAAAAE0ioAAAAAAJiWgAAAAAAAmJaAFwAAAAAAmJaAAAAAAACYloA=
    # SIGNATURE nsutxRIDOYMKmdAES/ogvlSW555S0jKcRqZtHR6MwFW1zXJ6kMZur26kdyYx89cEzD4z0iGEU2MpXvKCOUILBA==

    order_data = OrderSignatureRequest(
        op=RequestOperation.Order,
        # NOTE: This is the base64 of the above address
        account=base64.b64encode(signer.decoded_address()),
        sell_slot_id=42,
        buy_slot_id=23,
        sell_amount=10000000,
        buy_amount=10000000,
        max_sell_amount_from_pool=10000000,
        max_buy_amount_to_pool=10000000,
        expires_on=1234,
        nonce=1234,
    )

    expected_encoding = "BgOhB7/zzhC+HXDdGOdLwJln5NYwm6UNXx3chmQSVTG4AAAAAAAABNIAAAAAAAAE0ioAAAAAAJiWgAAAAAAAmJaAFwAAAAAAmJaAAAAAAACYloA="
    actual_encoding = base64.b64encode(encode_user_operation(order_data)).decode(
        "utf-8"
    )

    expected_sig = "nsutxRIDOYMKmdAES/ogvlSW555S0jKcRqZtHR6MwFW1zXJ6kMZur26kdyYx89cEzD4z0iGEU2MpXvKCOUILBA=="
    actual_sig = signer.sign_message(base64.b64decode(actual_encoding))

    print("ORDER DATA", order_data)
    print("ENCODED", actual_encoding)
    print("SIGNATURE", actual_sig)
    print()

    assert actual_encoding == expected_encoding
    assert expected_sig == actual_sig


def test_encode_cancel():
    cancel_data = CancelSignatureRequest(
        op=RequestOperation.Cancel,
        user="C3_AOQQPP7TZYIL4HLQ3UMOOS6ATFT6JVRQTOSQ2XY53SDGIESVGG4CJ7TS",
        creator="AOQQPP7TZYIL4HLQ3UMOOS6ATFT6JVRQTOSQ2XY53SDGIESVGG4MPFYUMQ",
        all_orders_until=12341234,
    )

    expected_encoding = b"12341234"
    actual_encoding = base64.b64encode(encode_user_operation(cancel_data))

    expected_sig = "7aG4bPe9O0fuCF7ln/l49D8zoqziyKIcR4A/lz1bmdprtIfBLAgwHsaovh8D0+LKDOWoBFGIotXXvhoQUy3WDQ=="
    actual_sig = signer.sign_message(base64.b64decode(actual_encoding))

    print("CANCEL", cancel_data)
    print("ENCODED", actual_encoding)
    print("SIGNATURE", actual_sig)
    print()

    assert actual_encoding == expected_encoding
    assert expected_sig == actual_sig


def test_encode_withdraw():
    # WITHDRAW {
    #   op: 'withdraw',
    #   assetId: 0,
    #   amount: 1234n,
    #   receiver: {
    #     chain: 'algorand',
    #     tokenAddress: 'AOQQPP7TZYIL4HLQ3UMOOS6ATFT6JVRQTOSQ2XY53SDGIESVGG4MPFYUMQ'
    #   },
    #   maxBorrow: 0n,
    #   maxFees: 10n
    # }
    # ENCODED AQAAAAAAAAAE0gAIA6EHv/POEL4dcN0Y50vAmWfk1jCbpQ1fHdyGZBJVMbgAAAAAAAAAAAAAAAAAAAAK
    # SIGNATURE q5VW3oEf6o6lk8qHeHYVAcUNe/kwuPKEIZxScm8M6quNoZ0DeavCnKkrxHuEjGDOK3ObHEity0z9JJYlV8psBg==

    withdraw_data = WithdrawSignatureRequest(
        op=RequestOperation.Withdraw,
        receiver=XChainAddress(
            chain_id=8,
            address=encoding.decode_address(
                "AOQQPP7TZYIL4HLQ3UMOOS6ATFT6JVRQTOSQ2XY53SDGIESVGG4MPFYUMQ",
            ),
        ),
        slot_id=0,
        amount=1234,
        max_borrow=0,
        max_fees=10,
    )

    expected_encoding = b"AQAAAAAAAAAE0gAIA6EHv/POEL4dcN0Y50vAmWfk1jCbpQ1fHdyGZBJVMbgAAAAAAAAAAAAAAAAAAAAK"
    actual_encoding = base64.b64encode(encode_user_operation(withdraw_data))

    expected_sig = "q5VW3oEf6o6lk8qHeHYVAcUNe/kwuPKEIZxScm8M6quNoZ0DeavCnKkrxHuEjGDOK3ObHEity0z9JJYlV8psBg=="
    actual_sig = signer.sign_message(base64.b64decode(actual_encoding))

    print("WITHDRAW", withdraw_data)
    print("ENCODED", actual_encoding)
    print("SIGNATURE", actual_sig)
    print()

    assert actual_encoding == expected_encoding
    assert expected_sig == actual_sig


def test_encode_lend():
    # LEND { op: 'lend', assetId: 0, amount: 1234n }
    # ENCODED AgAAAAAAAAAE0g==
    # SIGNATURE QeQc7Rz0P+kAye8tRX5ctzMNUvaU3duaof+Dkda/lNkji58Wzw6ajWIyITUvJVymH5ZjDx4KPxHcHyX+ganSAg==

    lend_data = LendSignatureRequest(
        op=RequestOperation.Lend,
        slot_id=0,
        amount=1234,
    )

    expected_encoding = b"AgAAAAAAAAAE0g=="
    actual_encoding = base64.b64encode(encode_user_operation(lend_data))

    expected_sig = "QeQc7Rz0P+kAye8tRX5ctzMNUvaU3duaof+Dkda/lNkji58Wzw6ajWIyITUvJVymH5ZjDx4KPxHcHyX+ganSAg=="
    actual_sig = signer.sign_message(base64.b64decode(actual_encoding))

    print("LEND", lend_data)
    print("ENCODED", actual_encoding)
    print("SIGNATURE", actual_sig)
    print()

    assert actual_encoding == expected_encoding
    assert expected_sig == actual_sig


def test_encode_redeem():
    # REDEEM { op: 'redeem', assetId: 0, amount: 1234n }
    # ENCODED AgD////////7Lg==
    # SIGNATURE 32jjXn114TRt0lNQ17abCrLU81HJX54Bg3AqemlEsc7nOjpNKbYKtD6mYeYWC7uXaikWwDQPZk2pg2EA1/aMBQ==

    redeem_data = CERedeemRequest(
        op=RequestOperation.Redeem,
        slot_id=0,
        amount=1234,
    )

    expected_encoding = b"AgD////////7Lg=="
    actual_encoding = base64.b64encode(encode_user_operation(redeem_data))

    expected_sig = "32jjXn114TRt0lNQ17abCrLU81HJX54Bg3AqemlEsc7nOjpNKbYKtD6mYeYWC7uXaikWwDQPZk2pg2EA1/aMBQ=="
    actual_sig = signer.sign_message(base64.b64decode(actual_encoding))

    print("REDEEM", redeem_data)
    print("ENCODED", actual_encoding)
    print("SIGNATURE", actual_sig)
    print()

    assert actual_encoding == expected_encoding
    assert expected_sig == actual_sig


def test_encode_borrow():
    # BORROW { op: 'borrow', assetId: 0, amount: 1234n }
    # ENCODED AgD////////7Lg==
    # SIGNATURE 32jjXn114TRt0lNQ17abCrLU81HJX54Bg3AqemlEsc7nOjpNKbYKtD6mYeYWC7uXaikWwDQPZk2pg2EA1/aMBQ==

    borrow_data = BorrowSignatureRequest(
        op=RequestOperation.Borrow,
        slot_id=0,
        amount=1234,
    )

    expected_encoding = b"AgD////////7Lg=="
    actual_encoding = base64.b64encode(encode_user_operation(borrow_data))

    expected_sig = "32jjXn114TRt0lNQ17abCrLU81HJX54Bg3AqemlEsc7nOjpNKbYKtD6mYeYWC7uXaikWwDQPZk2pg2EA1/aMBQ=="
    actual_sig = signer.sign_message(base64.b64decode(actual_encoding))

    print("BORROW", borrow_data)
    print("ENCODED", actual_encoding)
    print("SIGNATURE", actual_sig)
    print()

    assert actual_encoding == expected_encoding
    assert expected_sig == actual_sig


def test_encode_repay():
    # REPAY { op: 'repay', assetId: 0, amount: 1234n }
    # ENCODED AgAAAAAAAAAE0g==
    # SIGNATURE QeQc7Rz0P+kAye8tRX5ctzMNUvaU3duaof+Dkda/lNkji58Wzw6ajWIyITUvJVymH5ZjDx4KPxHcHyX+ganSAg==

    repay_data = RepaySignatureRequest(
        op=RequestOperation.Repay,
        slot_id=0,
        amount=1234,
    )

    expected_encoding = b"AgAAAAAAAAAE0g=="
    actual_encoding = base64.b64encode(encode_user_operation(repay_data))

    expected_sig = "QeQc7Rz0P+kAye8tRX5ctzMNUvaU3duaof+Dkda/lNkji58Wzw6ajWIyITUvJVymH5ZjDx4KPxHcHyX+ganSAg=="
    actual_sig = signer.sign_message(base64.b64decode(actual_encoding))

    print("REPAY", repay_data)
    print("ENCODED", actual_encoding)
    print("SIGNATURE", actual_sig)
    print()

    assert actual_encoding == expected_encoding
    assert expected_sig == actual_sig


def test_encode_liquidate():
    # LIQUIDATE {
    #   op: 'liquidate',
    #   target: 'AOQQPP7TZYIL4HLQ3UMOOS6ATFT6JVRQTOSQ2XY53SDGIESVGG4CJ7TS',
    #   cash: Map(1) { 0 => 1234n },
    #   pool: Map(1) { 0 => 1234n }
    # }
    # ENCODED BAOhB7/zzhC+HXDdGOdLwJln5NYwm6UNXx3chmQSVTG4ACUAMAABAAAAAAAAAATSAAEAAAAAAAAABNI=
    # SIGNATURE cL7hPWZSFR1hYG+qmzTOyh1lJASPCTDdL5Cd0n0pME9IN1dstoJ7f71ty1C9oCvqn08+tZTs4SWJG8xZj45uAg==

    liquidate_data = LiquidateSignatureRequest(
        op=RequestOperation.Liquidate,
        # FIXME: This is being encoded incorrectly
        target=base64.b64encode(signer.decoded_address()),
        cash={0: 1234},
        pool={0: 1234},
    )

    expected_encoding = b"BAOhB7/zzhC+HXDdGOdLwJln5NYwm6UNXx3chmQSVTG4ACUAMAABAAAAAAAAAATSAAEAAAAAAAAABNI="
    actual_encoding = base64.b64encode(encode_user_operation(liquidate_data))

    expected_sig = "cL7hPWZSFR1hYG+qmzTOyh1lJASPCTDdL5Cd0n0pME9IN1dstoJ7f71ty1C9oCvqn08+tZTs4SWJG8xZj45uAg=="
    actual_sig = signer.sign_message(base64.b64decode(actual_encoding))

    print("LIQUIDATE", liquidate_data)
    print("ENCODED", actual_encoding)
    print("SIGNATURE", actual_sig)
    print()

    assert actual_encoding == expected_encoding
    assert expected_sig == actual_sig


def test_encode_delegate():
    # DELEGATE {
    #   op: 'delegate',
    #   delegate: 'AOQQPP7TZYIL4HLQ3UMOOS6ATFT6JVRQTOSQ2XY53SDGIESVGG4MPFYUMQ',
    #   creation: 123456,
    #   expiration: 432100
    # }
    # ENCODED AwOhB7/zzhC+HXDdGOdLwJln5NYwm6UNXx3chmQSVTG4AAAAAAAB4kAAAAAAAAaX5A==
    # SIGNATURE 3WGn56p+Xi3ZRatxYdlJiqID8+dXEEbzFWNn+YVab7BDBVo2f8sTNHUhHvhaP8DIgH+ZBmkQRMvxylpNTlB5Ag==

    delegate_data = DelegateSignatureRequest(
        op=RequestOperation.Delegate,
        delegate=base64.b64encode(signer.decoded_address()),
        creation=123456,
        expiration=432100,
    )

    expected_encoding = (
        b"AwOhB7/zzhC+HXDdGOdLwJln5NYwm6UNXx3chmQSVTG4AAAAAAAB4kAAAAAAAAaX5A=="
    )
    actual_encoding = base64.b64encode(encode_user_operation(delegate_data))

    expected_sig = "3WGn56p+Xi3ZRatxYdlJiqID8+dXEEbzFWNn+YVab7BDBVo2f8sTNHUhHvhaP8DIgH+ZBmkQRMvxylpNTlB5Ag=="
    actual_sig = signer.sign_message(base64.b64decode(actual_encoding))

    print("DELEGATE", delegate_data)
    print("ENCODED", actual_encoding)
    print("SIGNATURE", actual_sig)
    print()

    assert actual_encoding == expected_encoding
    assert expected_sig == actual_sig


def test_encode_account_move():
    # ACCOUNT MOVE {
    #   op: 'account-move',
    #   target: 'AOQQPP7TZYIL4HLQ3UMOOS6ATFT6JVRQTOSQ2XY53SDGIESVGG4CJ7TS',
    #   cash: Map(1) { 0 => 1234n },
    #   pool: Map(1) { 0 => 1234n }
    # }
    # ENCODED BQOhB7/zzhC+HXDdGOdLwJln5NYwm6UNXx3chmQSVTG4ACUAMAABAAAAAAAAAATSAAEAAAAAAAAABNI=
    # SIGNATURE 21e+KKUQbUMeuuE98hL97TSDy7oXryXw4pNjvX3XfJioBTV5V/lcRHbq7O7IUoOZNxDg4menOI+1l3R3uB3dBQ==

    account_move_data = AccountMoveSignatureRequest(
        op=RequestOperation.AccountMove,
        target=base64.b64encode(signer.decoded_address()),
        cash={0: 1234},
        pool={0: 1234},
    )

    expected_encoding = b"BQOhB7/zzhC+HXDdGOdLwJln5NYwm6UNXx3chmQSVTG4ACUAMAABAAAAAAAAAATSAAEAAAAAAAAABNI="
    actual_encoding = base64.b64encode(encode_user_operation(account_move_data))

    expected_sig = "21e+KKUQbUMeuuE98hL97TSDy7oXryXw4pNjvX3XfJioBTV5V/lcRHbq7O7IUoOZNxDg4menOI+1l3R3uB3dBQ=="
    actual_sig = signer.sign_message(base64.b64decode(actual_encoding))

    print("ACCOUNT MOVE", account_move_data)
    print("ENCODED", actual_encoding)
    print("SIGNATURE", actual_sig)
    print()

    assert actual_encoding == expected_encoding
    assert expected_sig == actual_sig
