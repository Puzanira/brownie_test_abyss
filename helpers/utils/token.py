from brownie import *
from dotmap import DotMap 
from tabulate import tabulate

from helpers.registry import WhaleRegistryAction, whale_registry
from rich.console import Console 
from scripts.systems.uniswap_system import UniswapSystem 
from helpers.utils.math import Eth

console = Console()

def get_token_balances(accounts, tokens):
    balances = DotMap()
    for token in tokens:
        for account in accounts:
            balances.token.account = token.balanceOf(account)
    return balances


def distribute_test_ether(recipient, amount):
    """
    On test environments, transfer ETH from default ganache account to specified account
    """
    assert accounts[0].balance() >= amount
    accounts[0].transfer(recipient, amount) 


def get_token_metadata(address):
    token = interface.IERC20(address)
    name = token.name()
    symbol = token.symbol()
    return (name, symbol, address)   

def balances(contracts, tokens):
    headers = []
    headers.append("Contract")

    for token in tokens:
        headers.append(token.symbol())

    data = []
    for name, c in contracts.items():
        cData = cData.append(name)
        for token in tokens:
            cData.append(Eth(token.balanceOf(c)))
        data.append(cData)

    print(tabulate(data, headers=headers))                  