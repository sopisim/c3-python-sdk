import base64
from algosdk import encoding
from c3_signers.encode import OrderData, encode_order_data, encode_user_operation
from c3_signers.signers import AlgorandMessageSigner
from c3_signers.types import CEAccountMoveRequest, CEBorrowRequest, CEDelegateRequest, CELendRequest, CELiquidateRequest, CERedeemRequest, CERepayRequest, CERequestOp, CEWithdrawRequest, XChainAddress


def test_encode_order_data():
	# ORDER DATA {
	#   account: 'ooAKiQKqLxd/Iz9KSr5jw7EwEopLP+ATQ8MQVnCJvYU=',
	#   sellSlotId: 42,
	#   buySlotId: 23,
	#   sellAmount: 10000000n,
	#   buyAmount: 10000000n,
	#   maxBuyAmountToPool: 10000000n,
	#   maxSellAmountFromPool: 10000000n,
	#   expiresOn: 1234,
	#   nonce: 1234
	# }
	# ENCODED BqKACokCqi8XfyM/Skq+Y8OxMBKKSz/gE0PDEFZwib2FAAAAAAAABNIAAAAAAAAE0ioAAAAAAJiWgAAAAAAAmJaAFwAAAAAAmJaAAAAAAACYloA=
	# SIGNATURE 3vr2PfcnssAc5rs5sV2Y2snlaaAjor9xiok9Krll0EjeKCaeDgI1HZwwEnR3zbzKtJzlgneXmq/+Xk+lG1ulDw==

	order_data = OrderData(
		"ooAKiQKqLxd/Iz9KSr5jw7EwEopLP+ATQ8MQVnCJvYU=",
		42,
		23,
		10000000,
		10000000,
		10000000,
		10000000,
		1234,
		1234,
	)

	expected_encoding = b'BqKACokCqi8XfyM/Skq+Y8OxMBKKSz/gE0PDEFZwib2FAAAAAAAABNIAAAAAAAAE0ioAAAAAAJiWgAAAAAAAmJaAFwAAAAAAmJaAAAAAAACYloA='
	actual_encoding = base64.b64encode(encode_order_data(order_data))
	assert actual_encoding == expected_encoding

	signer = AlgorandMessageSigner(base64.b64encode(bytes(range(32))).decode('utf-8'))
	expected_sig = b'3vr2PfcnssAc5rs5sV2Y2snlaaAjor9xiok9Krll0EjeKCaeDgI1HZwwEnR3zbzKtJzlgneXmq/+Xk+lG1ulDw=='
	actual_sig = signer.sign_message(actual_encoding)
	print(actual_sig, expected_sig)
	#assert expected_sig == actual_sig

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

	withdraw_data = CEWithdrawRequest(
		op=CERequestOp.Withdraw,
		receiver=XChainAddress(
			chain_id=8,
			address=encoding.decode_address("AOQQPP7TZYIL4HLQ3UMOOS6ATFT6JVRQTOSQ2XY53SDGIESVGG4MPFYUMQ"),
		),
		slot_id=0,
		amount=1234,
		max_borrow=0,
		max_fees=10,
	)

	expected_encoding = b'AQAAAAAAAAAE0gAIA6EHv/POEL4dcN0Y50vAmWfk1jCbpQ1fHdyGZBJVMbgAAAAAAAAAAAAAAAAAAAAK'
	actual_encoding = base64.b64encode(encode_user_operation(withdraw_data))
	assert actual_encoding == expected_encoding

	signer = AlgorandMessageSigner(base64.b64encode(bytes(range(32))))
	expected_sig = b'q5VW3oEf6o6lk8qHeHYVAcUNe/kwuPKEIZxScm8M6quNoZ0DeavCnKkrxHuEjGDOK3ObHEity0z9JJYlV8psBg=='
	actual_sig = signer.sign_message(actual_encoding)
	print(actual_sig)
	#assert expected_sig == actual_sig

def test_encode_lend():
	# LEND { op: 'lend', assetId: 0, amount: 1234n }
	# ENCODED AgAAAAAAAAAE0g==
	# SIGNATURE QeQc7Rz0P+kAye8tRX5ctzMNUvaU3duaof+Dkda/lNkji58Wzw6ajWIyITUvJVymH5ZjDx4KPxHcHyX+ganSAg==

	lend_data = CELendRequest(
		op=CERequestOp.Lend,
		slot_id=0,
		amount=1234,
	)

	expected_encoding = b'AgAAAAAAAAAE0g=='
	actual_encoding = base64.b64encode(encode_user_operation(lend_data))
	assert actual_encoding == expected_encoding

	signer = AlgorandMessageSigner(base64.b64encode(bytes(range(32))))
	expected_sig = b'QeQc7Rz0P+kAye8tRX5ctzMNUvaU3duaof+Dkda/lNkji58Wzw6ajWIyITUvJVymH5ZjDx4KPxHcHyX+ganSAg=='
	actual_sig = signer.sign_message(actual_encoding)
	print(actual_sig)
	#assert expected_sig == actual_sig

def test_encode_redeem():
	# REDEEM { op: 'redeem', assetId: 0, amount: 1234n }
	# ENCODED AgD////////7Lg==
	# SIGNATURE 32jjXn114TRt0lNQ17abCrLU81HJX54Bg3AqemlEsc7nOjpNKbYKtD6mYeYWC7uXaikWwDQPZk2pg2EA1/aMBQ==

	redeem_data = CERedeemRequest(
		op=CERequestOp.Redeem,
		slot_id=0,
		amount=1234,
	)

	expected_encoding = b'AgD////////7Lg=='
	actual_encoding = base64.b64encode(encode_user_operation(redeem_data))
	assert actual_encoding == expected_encoding

	signer = AlgorandMessageSigner(base64.b64encode(bytes(range(32))))
	expected_sig = b'32jjXn114TRt0lNQ17abCrLU81HJX54Bg3AqemlEsc7nOjpNKbYKtD6mYeYWC7uXaikWwDQPZk2pg2EA1/aMBQ=='
	actual_sig = signer.sign_message(actual_encoding)
	print(actual_sig)
	#assert expected_sig == actual_sig

def test_encode_borrow():
	# BORROW { op: 'borrow', assetId: 0, amount: 1234n }
	# ENCODED AgD////////7Lg==
	# SIGNATURE 32jjXn114TRt0lNQ17abCrLU81HJX54Bg3AqemlEsc7nOjpNKbYKtD6mYeYWC7uXaikWwDQPZk2pg2EA1/aMBQ==

	borrow_data = CEBorrowRequest(
		op=CERequestOp.Borrow,
		slot_id=0,
		amount=1234,
	)

	expected_encoding = b'AgD////////7Lg=='
	actual_encoding = base64.b64encode(encode_user_operation(borrow_data))
	assert actual_encoding == expected_encoding

	signer = AlgorandMessageSigner(base64.b64encode(bytes(range(32))))
	expected_sig = b'32jjXn114TRt0lNQ17abCrLU81HJX54Bg3AqemlEsc7nOjpNKbYKtD6mYeYWC7uXaikWwDQPZk2pg2EA1/aMBQ=='
	actual_sig = signer.sign_message(actual_encoding)
	print(actual_sig)
	#assert expected_sig == actual_sig

def test_encode_repay():
	# REPAY { op: 'repay', assetId: 0, amount: 1234n }
	# ENCODED AgAAAAAAAAAE0g==
	# SIGNATURE QeQc7Rz0P+kAye8tRX5ctzMNUvaU3duaof+Dkda/lNkji58Wzw6ajWIyITUvJVymH5ZjDx4KPxHcHyX+ganSAg==

	repay_data = CERepayRequest(
		op=CERequestOp.Repay,
		slot_id=0,
		amount=1234,
	)

	expected_encoding = b'AgAAAAAAAAAE0g=='
	actual_encoding = base64.b64encode(encode_user_operation(repay_data))
	assert actual_encoding == expected_encoding

	signer = AlgorandMessageSigner(base64.b64encode(bytes(range(32))))
	expected_sig = b'QeQc7Rz0P+kAye8tRX5ctzMNUvaU3duaof+Dkda/lNkji58Wzw6ajWIyITUvJVymH5ZjDx4KPxHcHyX+ganSAg=='
	actual_sig = signer.sign_message(actual_encoding)
	print(actual_sig)
	#assert expected_sig == actual_sig

def test_encode_liquidate():
	# LIQUIDATE {
	#   op: 'liquidate',
	#   target: 'C3_AOQQPP7TZYIL4HLQ3UMOOS6ATFT6JVRQTOSQ2XY53SDGIESVGG4CJ7TS',
	#   cash: Map(1) { 0 => 1234n },
	#   pool: Map(1) { 0 => 1234n }
	# }
	# ENCODED BAOhB7/zzhC+HXDdGOdLwJln5NYwm6UNXx3chmQSVTG4ACUAMAABAAAAAAAAAATSAAEAAAAAAAAABNI=
	# SIGNATURE cL7hPWZSFR1hYG+qmzTOyh1lJASPCTDdL5Cd0n0pME9IN1dstoJ7f71ty1C9oCvqn08+tZTs4SWJG8xZj45uAg==

	signer = AlgorandMessageSigner(base64.b64encode(bytes(range(32))).decode('utf-8'))
	liquidate_data = CELiquidateRequest(
		op=CERequestOp.Liquidate,
		# FIXME: This is being encoded incorrectly
		target=base64.b64encode(signer.public_key()),
		cash={0: 1234},
		pool={0: 1234},
	)

	expected_encoding = b'BAOhB7/zzhC+HXDdGOdLwJln5NYwm6UNXx3chmQSVTG4ACUAMAABAAAAAAAAAATSAAEAAAAAAAAABNI='
	actual_encoding = base64.b64encode(encode_user_operation(liquidate_data))
	#assert actual_encoding == expected_encoding

	expected_sig = b'cL7hPWZSFR1hYG+qmzTOyh1lJASPCTDdL5Cd0n0pME9IN1dstoJ7f71ty1C9oCvqn08+tZTs4SWJG8xZj45uAg=='
	actual_sig = signer.sign_message(actual_encoding)
	print(actual_sig)
	#assert expected_sig == actual_sig

def test_encode_delegate():
	# DELEGATE {
	#   op: 'delegate',
	#   delegate: 'AOQQPP7TZYIL4HLQ3UMOOS6ATFT6JVRQTOSQ2XY53SDGIESVGG4MPFYUMQ',
	#   creation: 123456,
	#   expiration: 432100
	# }
	# ENCODED AwOhB7/zzhC+HXDdGOdLwJln5NYwm6UNXx3chmQSVTG4AAAAAAAB4kAAAAAAAAaX5A==
	# SIGNATURE 3WGn56p+Xi3ZRatxYdlJiqID8+dXEEbzFWNn+YVab7BDBVo2f8sTNHUhHvhaP8DIgH+ZBmkQRMvxylpNTlB5Ag==

	delegate_data = CEDelegateRequest(
		op=CERequestOp.Delegate,
		delegate='AOQQPP7TZYIL4HLQ3UMOOS6ATFT6JVRQTOSQ2XY53SDGIESVGG4MPFYUMQ',
		creation=123456,
		expiration=432100,
	)

	expected_encoding = b'AwOhB7/zzhC+HXDdGOdLwJln5NYwm6UNXx3chmQSVTG4AAAAAAAB4kAAAAAAAAaX5A=='
	actual_encoding = base64.b64encode(encode_user_operation(delegate_data))
	assert actual_encoding == expected_encoding

	signer = AlgorandMessageSigner(base64.b64encode(bytes(range(32))))
	expected_sig = b'3WGn56p+Xi3ZRatxYdlJiqID8+dXEEbzFWNn+YVab7BDBVo2f8sTNHUhHvhaP8DIgH+ZBmkQRMvxylpNTlB5Ag=='
	actual_sig = signer.sign_message(actual_encoding)
	print(actual_sig)
	#assert expected_sig == actual_sig

def test_encode_account_move():
	# ACCOUNT MOVE {
	#   op: 'account-move',
	#   target: 'C3_AOQQPP7TZYIL4HLQ3UMOOS6ATFT6JVRQTOSQ2XY53SDGIESVGG4CJ7TS',
	#   cash: Map(1) { 0 => 1234n },
	#   pool: Map(1) { 0 => 1234n }
	# }
	# ENCODED BQOhB7/zzhC+HXDdGOdLwJln5NYwm6UNXx3chmQSVTG4ACUAMAABAAAAAAAAAATSAAEAAAAAAAAABNI=
	# SIGNATURE 21e+KKUQbUMeuuE98hL97TSDy7oXryXw4pNjvX3XfJioBTV5V/lcRHbq7O7IUoOZNxDg4menOI+1l3R3uB3dBQ==

	account_move_data = CEAccountMoveRequest(
		op=CERequestOp.AccountMove,
		target='C3_AOQQPP7TZYIL4HLQ3UMOOS6ATFT6JVRQTOSQ2XY53SDGIESVGG4CJ7TS',
		cash={0: 1234},
		pool={0: 1234},
	)

	expected_encoding = b'BQOhB7/zzhC+HXDdGOdLwJln5NYwm6UNXx3chmQSVTG4ACUAMAABAAAAAAAAAATSAAEAAAAAAAAABNI='
	actual_encoding = base64.b64encode(encode_user_operation(account_move_data))
	assert actual_encoding == expected_encoding

	signer = AlgorandMessageSigner(base64.b64encode(bytes(range(32))))
	expected_sig = b'21e+KKUQbUMeuuE98hL97TSDy7oXryXw4pNjvX3XfJioBTV5V/lcRHbq7O7IUoOZNxDg4menOI+1l3R3uB3dBQ=='
	actual_sig = signer.sign_message(actual_encoding)
	print(actual_sig)
	#assert expected_sig == actual_sig
