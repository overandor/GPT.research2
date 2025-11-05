# flashloan/cli.py

import os
import click
from web3 import Web3
from .client import LP_FLASH_LOANER_ABI, FLASH_LP_WRAPPER_ABI

def get_w3():
    provider = os.environ.get('PROVIDER', 'http://localhost:8545')
    return Web3(Web3.HTTPProvider(provider))

@click.group()
def cli():
    pass

@cli.command()
@click.option('--wrapper-address', required=True, help='The address of the FlashLPWrapper contract.')
@click.option('--amount', required=True, type=float, help='The amount of LP tokens to wrap.')
def wrap_lp(wrapper_address, amount):
    """Wraps an LP token to make it flash-loanable."""
    w3 = get_w3()
    private_key = os.environ.get('PRIVATE_KEY')
    if not private_key:
        print("Please set the PRIVATE_KEY environment variable.")
        return

    account = w3.eth.account.from_key(private_key)
    wrapper_contract = w3.eth.contract(address=wrapper_address, abi=FLASH_LP_WRAPPER_ABI)

    amount_in_wei = w3.to_wei(amount, 'ether')

    tx = wrapper_contract.functions.deposit(amount_in_wei).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
    })

    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"Wrapping {amount}... Transaction hash: {tx_hash.hex()}")

@cli.command()
@click.option('--loaner-address', required=True, help='The address of the LPFlashLoaner contract.')
@click.option('--executor', required=True, help='The address of the executor contract.')
@click.option('--data', default='', help='The data to pass to the executor.')
def flash_loan(loaner_address, executor, data):
    """Executes a flash loan."""
    w3 = get_w3()
    private_key = os.environ.get('PRIVATE_KEY')
    if not private_key:
        print("Please set the PRIVATE_KEY environment variable.")
        return

    account = w3.eth.account.from_key(private_key)
    loaner_contract = w3.eth.contract(address=loaner_address, abi=LP_FLASH_LOANER_ABI)

    tx = loaner_contract.functions.executeFlashLoan(executor, data.encode()).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
    })

    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"Executing flash loan... Transaction hash: {tx_hash.hex()}")

@cli.command()
@click.option('--token', required=True, help='The address of the token to check.')
@click.option('--owner', default='self', help='The address of the owner to check.')
def get_balance(token, owner):
    """Gets the balance of a token for a given owner."""
    w3 = get_w3()
    private_key = os.environ.get('PRIVATE_KEY')
    if owner == 'self':
        if not private_key:
            print("Please set the PRIVATE_KEY environment variable to use 'self'.")
            return
        owner = w3.eth.account.from_key(private_key).address

    # A generic ERC20 ABI is needed here. For now, we'll use the wrapper ABI as a stand-in
    # as it has the `balanceOf` function.
    token_contract = w3.eth.contract(address=token, abi=FLASH_LP_WRAPPER_ABI)
    balance = token_contract.functions.balanceOf(owner).call()
    balance_in_ether = w3.from_wei(balance, 'ether')
    print(f"Balance of {token} for {owner}: {balance_in_ether}")

if __name__ == '__main__':
    cli()
