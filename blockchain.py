from web3 import Web3
import json

# =============================
# CONNECT GANACHE
# =============================

GANACHE_URL = "http://127.0.0.1:7545"

w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

if not w3.is_connected():
    raise Exception("❌ Ganache blockchain not connected")


contract_address = Web3.to_checksum_address(
    "0xF020Bcb4a549DC3594F5b136F39053a800A69C7D"
)

contract_abi = json.loads(""" [
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "filename",
				"type": "string"
			},
			{
				"internalType": "address",
				"name": "user",
				"type": "address"
			}
		],
		"name": "grantAccess",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "filename",
				"type": "string"
			}
		],
		"name": "uploadFile",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			},
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"name": "access",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "filename",
				"type": "string"
			},
			{
				"internalType": "address",
				"name": "user",
				"type": "address"
			}
		],
		"name": "checkAccess",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"name": "fileOwner",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "owner",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
] """)

contract = w3.eth.contract(
    address=contract_address,
    abi=contract_abi
)

OWNER_ADDRESS = Web3.to_checksum_address(
    "0xEa23e87EB9B571009A508f6b51ef4Fe1a91E5919"
)


# =============================
# VERIFY WALLET EXISTS
# =============================

def verify_wallet(address):

    try:

        address = Web3.to_checksum_address(address)

        accounts = w3.eth.accounts

        return address in accounts

    except:
        return False


# =============================
# FILE UPLOAD
# =============================

def upload_file_to_blockchain(filename):

    try:

        tx = contract.functions.uploadFile(filename).transact({
            "from": OWNER_ADDRESS
        })

        receipt = w3.eth.wait_for_transaction_receipt(tx)

        print("✅ File registered on blockchain")

        return receipt.transactionHash.hex()

    except Exception as e:
        print("Blockchain Upload Error:", e)
        raise


# =============================
# GRANT ACCESS
# =============================

def grant_access(filename, user_address):

    try:

        user_address = Web3.to_checksum_address(user_address)

        tx = contract.functions.grantAccess(
            filename,
            user_address
        ).transact({
            "from": OWNER_ADDRESS
        })

        w3.eth.wait_for_transaction_receipt(tx)

        print("✅ Access granted")

    except Exception as e:
        print("Grant Access Error:", e)
        raise


# =============================
# CHECK ACCESS
# =============================

def check_access(filename, user_address):

    try:

        user_address = Web3.to_checksum_address(user_address)

        return contract.functions.checkAccess(
            filename,
            user_address
        ).call()

    except Exception as e:

        print("Access Check Error:", e)

        return False
