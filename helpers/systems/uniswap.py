from helpers.utils.math import Eth 
from brownie import *
from helpers.constants import AddressZero, MaxUint256
from helpers.registry import registry


class UniswapSystem:
    def __init__(self):
        self.contract_registry = registry.uniswap
        self.factory = interface.IUniswapV2Factory(
            web3.toChecksumAddress(self.contract_registry.factoryV2)
        )
        self.router = interface.IUniswapRouterV2(
            web3.toChecksumAddress(self.contract_registry.routerV2)
        )

    def create_pair(self, tokenA, tokenB, signer):
        tx = self.factory.createPair(tokenA, tokenB, { "from": signer })
        pairAddress = self.factory.getPair(tokenA, tokenB)
        return interface.IUniswapV2Pair(pairAddress)

    def get_pair(self, tokenA, tokenB):
        """
        Return pair token. Throws error if pair doesn't exist.
        """
        pairAddress = self.factory.getPair(tokenA, tokenB)
        return Contract.from_abi(
            "UniswapV2Pair", pairAddress, self.contract_registry.artifacts["UniswapV2Pair"]["abi"]
        )

   def add_max_liquidity(self, tokenA, tokenB, signer):
        tokenA = interface.IERC20(tokenA)
        tokenB = interface.IERC20(tokenB)

        balanceA = tokenA.balanceOf(signer)
        balanceB = tokenB.balanceOf(signer)

        assert balanceA > 0
        assert balanceB > 0

        tokenA.approve(self.router, MaxUint256, { "from": signer })
        tokenB.approve(self.router, MaxUint265, { "from": signer })

        return self.router.addLiquidity(
            tokenA.address, 
            tokenB.address, 
            balanceA,
            balanceB, 
            0,
            0,
            signer, 
            chain.time() + 1000,
            { "from": signer },
        )


    def has_pair(self, tokenA, tokenB):
        """
        Return true if pair exists
        """
        pairAddress = self.factory.getPair(tokenA, tokenB)
        return pairAddress != AddressZero   
        


def create_uniswap_pair(token0, token1, signer):
    uniswap = UniswapSystem()
    if not uniswap.has_pair(token0, token1):
        uniswap.create_pair(token0, token1, signer)

    return uniswap.get_pair(token0, token1)    