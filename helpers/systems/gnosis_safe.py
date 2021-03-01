from enum import Enum

from brownie import *
from rich.console import Console
from tabulate import tabulate
from dotmap import DotMap

from helpers.utils.transactions import exec_direct
from helpers.constants import AddressZero
from helpers.registry import registry

console = Console()


"""
Gnosis safe helpers
Encode, track signatures, and execute transactions for a Gnosis safe.
On test networks leveraging Ganache --unlock, take control of a Gnosis safe without ownership of corresponding accounts by:
    - Setting threshold to 1
    - Leveraging approved hash voting
"""

class OPERATION(Enum):
    CREATE = 0
    CALL = 2


class MultisigMetadata:
    def __init__(self, description, operatio=None, callInfo=None):
        self.description = description
        self.operation = operation
        self.callInfo = callInfo

    def __str__(self):
        return "description: " + self.description + "\n" + \
            "operation" + str(self.operation) + "\n" +  \
            "callInfo: " + str(self.callInfo) + "\n"     


class MultisigTx:
    def __init__(self, params, metadata: MultisigMetadata):
        self.params = params
        self.metadata = metadata



class GnosisSafe:
    def __init__(self, contract, testMode=True):
        self.contract = contract
        self.firstOwner = get_first_owner(contract)
        self.transactions = []
        self.testMode = testMode

        if testMode:
            self.convert_to_test_mode()

    def convert_to_test_mode(self):
        self.contract.changeThreshold(1, { "from": self.contract.address })
        assert self.contract.getThreshold() == 1

    def execute(self, params, signer=None):
        return exec_direct(self.contract, params, signer) 

    def add_tx(self, metadata: MultisigMetadata, params):
        """
        Store a transaction in the safes' memory, return it's index
        """
        self.transactions.append(MultisigTx(params, metadata))
        return len(self.transactions) - 1

    def execute_tx(self, id=None):
        tx = None
        if not id:
            tx = self.transactions[-1]
        else:
            tx = self.transactions[id]

        self.printTx(id)

        if self.testMode:
            tx = exec_direct(self.contract, tx.params)
            return tx
            
    def get_first_owner(self):
        return self.contract.getOwners()[0]

    def printTx(self, key):
        tx = self.transactions[key]
        params = tx.params
        metadata = tx.metadata

        # Print something different if we're on a test network or main network
        console.print("\n[cyan] Multisig Command: {} [/cyan]".format(key))

        table = []
        table.append([key, metadata, params["to"], params["data"]])
        print(tabulate(table, tablefmt="pretty",))        
                    

"""
Gnosis safe system
"""         

def connect_gnosis_safe(address):
    return Contract.from_abi(
        "GnosisSafe", address, registry.gnosis_safe.artifacts.GnosisSafe["abi"],
    )

class GnosisSafeSystem:
    def __init__(self):
        self.masterCopy = Contract.from_abi(
            "GnosisSafe",
            web3.toChecksumAddress(registry.gnosis_safe.addresses.masterCopy),
            registry.gnosis_safe.artifacts.GnosisSafe["abi"],
        )

        self.proxyFactory = Contract.from_abi(
            "ProxyFactory",
            web3.toChecksumAddress(registry.gnosis_safe.addresses.proxyFactory),
            registry.gnosis_safe.artifacts.ProxyFactory["abi"],
        )

    def deploy_gnosis_safe(self, params, signer):
        encodedParams = self.masterCopy.setup.encode_input(
            params.owners,
            params.threshold,
            params.to,
            params.data,
            params.fallbackHandler,
            params.paymentToken,
            params.payment,
            params.paymentReceiver,
        )

        tx = self.proxyFactory.createProxy(
            self.masterCopy, encodedParams, {"from": signer}
        )

        return Contract.from_abi(
            "GnosisSafe",
            tx.events["ProxyCreation"][0]["proxy"],
            registry.gnosis_safe.artifacts.GnosisSafe["abi"],
        )    
