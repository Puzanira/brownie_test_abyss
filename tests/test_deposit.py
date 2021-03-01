import pytest

from brownie import Token, AbyssLockup, AbyssSafeBase, accounts

zero_address = '0x0000000000000000000000000000000000000000'
decimals = 1e18

def adjust_amount(amount):
    return amount * decimals


def test_deflation():
    defl_token = accounts[0].deploy(Token, 1000, 10) # 10% deflation
    defl_token.transfer(accounts[1], 100, {'from': accounts[0]})

    assert defl_token.balanceOf(accounts[1]) == 90


def print_state(abyss_safe, abyss_lockup, token, accounts):
    print("\n>>> =============================================================================================================== <<<\n")

    print("Safe1 Balance: {}\n".format(token.balanceOf(abyss_safe)))
    print("Safe1 Deposited / DivFactor: {} / {}\n\n".format(abyss_safe.totalDeposited(token), abyss_safe.totalDivFactorDeposited(token)))

    print("Lockup Balance:: {}\n".format(token.balanceOf(abyss_lockup)))
    print("Lockup Deposited / DivFactor: {} / {}\n\n".format(abyss_lockup.deposited(token), abyss_lockup.divFactor(token)))

    print("Safe1 Requested / DivFactor: {} / {}\n\n".format(abyss_safe.totalRequested(token), abyss_safe.totalDivFactorRequested(token)))

    print("\n")
    for account in accounts:
        print("Account {} - Deposited: {} / {}\n".format(account, abyss_safe.deposited(account, token), abyss_safe.divFactorDeposited(account, token)))

    print("\n")
    for account in accounts:
        print("Account {} - Requested: {} / {}\n".format(account, abyss_safe.requested(account, token), abyss_safe.divFactorRequested(account, token)))

    print("\n")
    for account in accounts:
        print("Account {} - Balance: {}\n".format(account, token.balanceOf(account)))

    print("\n>>> =============================================================================================================== <<<\n")

def test_deposit():
    abyss_token = accounts[0].deploy(Token, adjust_amount(1e30), 0) # 0 % deflation
    defl_token = accounts[0].deploy(Token, adjust_amount(1e30), 10) # 10% deflation

    abyss_lockup = accounts[0].deploy(AbyssLockup, 0)
    abyss_safe = accounts[0].deploy(AbyssSafeBase, abyss_token, abyss_lockup, 0, 0)

    abyss_lockup.initialize(abyss_safe, zero_address, zero_address, zero_address, {'from': accounts[0]})

    testing_accounts = accounts[1:4]
    deposit = 9000000000000000000000000

    # distribution && approves
    for account in testing_accounts:
        defl_token.transfer(account, adjust_amount(10e7), {'from': accounts[0]})
        defl_token.approve(abyss_lockup, adjust_amount(1e30), {'from': account})

#        print_state(abyss_safe, abyss_lockup, defl_token, testing_accounts)

        assert defl_token.balanceOf(account) == adjust_amount(10e7 * 90 / 100), "wrong distribution"

    # deposits
    deposited = {}
    balance_before = {}
    for account in testing_accounts:
        balance_before[account] = defl_token.balanceOf(account)
        abyss_safe.deposit(defl_token, deposit, account, {'from': account})#.info()
        deposited[account] = deposit

#        print_state(abyss_safe, abyss_lockup, defl_token, testing_accounts)
        assert abyss_safe.deposited(account, defl_token) == deposit * 90 // 100, "wrong deposited amount"

#        deposit /= 100

    #print_state(abyss_safe, abyss_lockup, defl_token, testing_accounts)
    # smbdy put money to contract directly
    defl_token.transfer(abyss_safe, adjust_amount(1e10), {'from': accounts[0]})
#    defl_token.transfer(abyss_lockup, adjust_amount(1e7), {'from': accounts[0]})

    print_state(abyss_safe, abyss_lockup, defl_token, testing_accounts)
#    print_state(abyss_safe, abyss_lockup, defl_token, testing_accounts)

    for account in testing_accounts:
        before = defl_token.balanceOf(account)
        abyss_safe.request(defl_token, deposited[account], {'from': account})#.info()
        print_state(abyss_safe, abyss_lockup, defl_token, testing_accounts)
        abyss_safe.withdraw(defl_token, {'from': account})#.info()
        print_state(abyss_safe, abyss_lockup, defl_token, testing_accounts)

        balance = defl_token.balanceOf(account)
        withdrawn = balance - before
        print("Account: {}, initial deposit: {}, withdrawn: {}, lost: {:.2f}%".format(account, deposited[account], withdrawn, 100 - withdrawn / deposited[account] * 100))
        print("\n>>> =============================================================================================================== <<<\n")



    print_state(abyss_safe, abyss_lockup, defl_token, testing_accounts)