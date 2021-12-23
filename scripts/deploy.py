from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

with open("../contracts/Token.sol") as file:
    token_file = file.read()

print("Installing...")
install_solc("0.7.0")


# Solidity source code
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"Token.sol": {"content": token_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.7.0",
)

with open("../contracts/compiled_sol.json", "w") as file:
    json.dump(compiled_sol, file)

bytecode = compiled_sol["contracts"]["Token.sol"]["Token"]["evm"]["bytecode"]["object"]

abi = json.loads(compiled_sol["contracts"]["Token.sol"]["Token"]["metadata"])["output"][
    "abi"
]

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
chain_id = 1337
my_address = "0x8EEB26040559413929a32f7F98b04b6d5C795573"
private_key = os.getenv("PRIVATE_KEY")
print(private_key)
Token = w3.eth.contract(abi=abi, bytecode=bytecode)

nonce = w3.eth.getTransactionCount(my_address)
print(nonce)
transaction = Token.constructor().buildTransaction(
    {
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
    }
)

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
# print(transaction)

txnHash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

transactionReceipt = w3.eth.wait_for_transaction_receipt(txnHash)
print(f"Done! Contract deployed to {transactionReceipt.contractAddress}")

token = w3.eth.contract(abi=abi, address=transactionReceipt.contractAddress)

print(f"Token name : {token.functions.name().call()}")
print(f"Token Symbol : {token.functions.symbol().call()}")
print(f"Total Supply of tokens : {token.functions.totalSupply().call()}")

howManytokens = 10
print(f"\nTransferring {howManytokens} tokens...")

tokenTransfertxn = token.functions.transfer(
    "0xA160e1cD3d43CDEfaD5584dD5E71CC2859d2a0Dc", howManytokens
).buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce + 1,
    }
)
signedtokenTransaferTxn = w3.eth.account.sign_transaction(
    tokenTransfertxn, private_key=private_key
)

txtokenTransferHash = w3.eth.send_raw_transaction(signedtokenTransaferTxn.rawTransaction)

print("Transffered!")
tokenTxnReceipt = w3.eth.wait_for_transaction_receipt(txtokenTransferHash)
print(token.functions.balanceOf("0xA160e1cD3d43CDEfaD5584dD5E71CC2859d2a0Dc").call())
