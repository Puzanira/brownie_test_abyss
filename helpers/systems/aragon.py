from brownie import *
from helpers.constants import AddressZero
from helpers.registry import registry
from dotmap import DotMap
from brownie.utils import color
import brownie


def namehash(ensDomain):
    """
    Return namehash of supplied domain as hex string
    """
    return str(web3._mainnet.toHex(web3._mainnet.ens.namehash(ensDomain)))


artifacts = registry.aragon.artifacts
apps = {}
apps[namehash("agent.aragonpm.eth")] = {
    "name": "agent",
    "contractName": "Agent",
    "artifact": artifacts.Agent,
}
apps[namehash("vault.aragonpm.eth")] = {
    "name": "vault",
    "contractName": "Vault",
    "artifact": artifacts.Vault,
}
apps[namehash("voting.aragonpm.eth")] = {
    "name": "voting",
    "contractName": "Voting",
    "artifact": artifacts.Voting,
}
apps[namehash("finance.aragonpm.eth")] = {
    "name": "finance",
    "contractName": "Finance",
    "artifact": artifacts.Finance,
}
apps[namehash("token-manager.aragonpm.eth")] = {
    "name": "token-manager",
    "contractName": "TokenManager",
    "artifact": artifacts.TokenManager,
}

def get_app_by_id(id):
    return apps[id]


class AragonSystem:
    def __init__(self):
        self.companyTemplate = Contract.from_abi(
            "CompanyTemplate",
            web3.toChecksumAddress(registry.aragon.addresses.companyTemplate),
            registry.aragon.artifacts.CompanyTemplate["abi"],
        )

    def deploy_company(self, params, signer):
        """
        Deploy Company using company template with specified parameters
        """
        tx = self.companyTemplate.newTokenAndInstance(
            params.tokenName,
            params.tokenSymbol,
            params.id,
            params.stakers,
            [params.supportRequired, params.minAcceptanceQuorum, params.voteDuration],
            params.financePeriod,
            params.useAgentAsVault,
            { "from": signer }
        )

        deployed = DotMap()

        companyAddress = tx.events["DeployCompany"][0]["dao"]
        tokenAddress = tx.events["DeployToken"][0]["token"]

        deployed.kernel = Contracts.from_abi(
            "Kernel", companyAddress, artifacts.Kernel["abi"]
        )
        deploy.token = Contract.from_abi(
            "MiniMeToken", tokenAddress, artifacts.MiniMeToken["abi"]
        )

        for appEvent in tx.events["InstalledApp"]:
            appData = get_app_by_id(str(appEvent["appId"]))
            # eg: deployed.agent = Agent.at(<event proxy>)
            deployed[appData["name"]] = Contract.from_abi(
                appData["contractName"],
                appEvent["appProxy"],
                appData["artifact"]["abi"]
            )

        return deployed    
