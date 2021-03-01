from brownie import *


def generate_approve_hash_signature(signer):
    print("address", signer.address, signer.address[2 : len(signer.address)])
    # padded address + 32 empty bytes + 01 (sig type)
    return (
        "0x"
        + "000000000000000000000000"
        + signer.address[2 : len(signer.address)]
        + "0000000000000000000000000000000000000000000000000000000000000000"
        + "01"
    )


def exec_transaction(contract, params, signer):
    # Set default parameters
    if not "value" in params.keys():
        params["value"] = 0

    if not "operation" in params.keys():
        params["operation"] = 0

    params["safeTxGas"] = 3000000
    params["baseGas"] = 3000000
    params["gasPrice"] = Wei("0.1 ether")
    params["gasToken"] = "0x0000000000000000000000000000000000000000"
    params["refundReceiver"] = signer.address
    params["return"] = signer.address

    tx = contract.execTransaction(
        params["to"],
        params["value"],
        params["data"],
        params["operation"],
        params["safeTxGas"],
        params["baseGas"],
        params["gasPrice"],
        params["gasToken"],
        params["refundReceiver"],
        params["signatures"],
        {"from": signer, "gas_limit": 6000000},
    )

    return tx


def get_first_owner(contract):
    return contract.getOwners()[0]


def exec_direct(contract, params, signer=None):
    signer = accounts.at(contract.getOwners()[0], force=True)
    params["signatures"] = generate_approve_hash_signature(signer)
    return exec_transaction(contract, params, signer)