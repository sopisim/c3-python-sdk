from c3_signers.sign_order_data import OrderData, encode_order_data


def test_encode_order_data():
	# Validate order data
	#
	# {                                                                                               
	#   account: 'vmvCyFq7tu+IeI3wGFBwo9t0wNrXRowAPrxKLPIN9Ns=',
	#   sellSlotId: 42,
	#   buySlotId: 23,
	#   sellAmount: 10000000n,
	#   buyAmount: 10000000n,
	#   maxBuyAmountToPool: 10000000n,
	#   maxSellAmountFromPool: 10000000n,
	#   expiresOn: 1234,
	#   nonce: 1234,
	# }
	# 
	# Encodes to
	#
	# Base64: BrIparUHhf7caGW/kNP5yjTxAiFsjN4naMdUfTHZy976AAAAAAAABNIAAAAAAAAE0ioAAAAAAJiWgAAAAAAAmJaAFwAAAAAAmJaAAAAAAACYloA=

	order_data = OrderData(
		"vmvCyFq7tu+IeI3wGFBwo9t0wNrXRowAPrxKLPIN9Ns=",
		42,
		23,
		10000000,
		10000000,
		10000000,
		10000000,
		1234,
		1234,
	)

	expected_encoding = "BrIparUHhf7caGW/kNP5yjTxAiFsjN4naMdUfTHZy976AAAAAAAABNIAAAAAAAAE0ioAAAAAAJiWgAAAAAAAmJaAFwAAAAAAmJaAAAAAAACYloA="

	assert encode_order_data(order_data) == expected_encoding

test_encode_order_data()
