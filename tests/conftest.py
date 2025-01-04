import os
import sys
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from scripts import constants

class Sandbox:
    def __init__(self, project, deployer):
        self.project = project
        self.deployer = deployer
        self._contracts = {}  # Dictionary to cache deployed contracts

    def deploy_finder_contract(self):
        if "finder_contract" not in self._contracts:
            self._contracts["finder_contract"] = self.deployer.deploy(self.project.FinderContract)

    def deploy_store_contract(self):
        if "store_contract" not in self._contracts:
            self._contracts["store_contract"] = self.deployer.deploy(
                self.project.StoreContract,
                constants.fixed_oracle_fee,
                constants.weekly_delay_fee,
                constants.empty_address,
            )
    
    def deploy_ancillary_interface(self):
        if "ancillary_interface" not in self._contracts:
            self._contracts["ancillary_interface"] = self.deployer.deploy(
                self.project.AncillaryDataInterface
            )

    def deploy_currency(self):
        if "currency" not in self._contracts:
            self._contracts["currency"] = self.deployer.deploy(
                self.project.TestERC20,
                "Test ERC20",
                "TT",
                18
            )

    def deploy_address_whitelist(self):
        if "address_whitelist" not in self._contracts:
            self._contracts["address_whitelist"] = self.deployer.deploy(self.project.AddressWhitelistContract)

    def deploy_identifier_whitelist(self):
        if "identifier_whitelist" not in self._contracts:
            self._contracts["identifier_whitelist"] = self.deployer.deploy(self.project.IdentifierWhitelistContract)

    def deploy_mock_oracle(self):
        if "mock_oracle" not in self._contracts:
            finder = self._contracts["finder_contract"]
            self._contracts["mock_oracle"] = self.deployer.deploy(
                self.project.MockAncillaryContract,
                finder.address,
                constants.empty_address,
            )
    
    def register_contracts(self):
        store = self._contracts["store_contract"]
        finder = self._contracts["finder_contract"]
        whitelist = self._contracts["address_whitelist"]
        identifier = self._contracts["identifier_whitelist"]
        mock = self._contracts["mock_oracle"]
        currency = self._contracts["currency"]

        finder.changeImplementationAddress(
            constants.Store,
            store.address,
            sender=self.deployer
        )
        finder.changeImplementationAddress(
            constants.CollateralWhitelist,
            whitelist.address,
            sender=self.deployer
        )
        finder.changeImplementationAddress(
            constants.IdentifierWhitelist,
            identifier.address,
            sender=self.deployer
        )
        finder.changeImplementationAddress(
            constants.Oracle,
            mock.address,
            sender=self.deployer,
        )
        whitelist.addToWhitelist(
            currency.address,
            sender=self.deployer,
        )
        identifier.addSupportedIdentifier(
            constants.default_identifier,
            sender=self.deployer,
        )
        final_fee = {"rawValue": int(constants.minimum_bond / 2)}
        store.setFinalFee(
            currency.address,
            final_fee,
            sender=self.deployer,
        )

    def deploy_optimistic_oracle_v3(self):
        if "optimistic_oracle_v3" not in self._contracts:

            finder = self._contracts["finder_contract"]
            currency = self._contracts["currency"]

            self._contracts["optimistic_oracle_v3"] = self.deployer.deploy(
                self.project.OOV3,
                finder.address,
                currency.address,
                constants.default_liveness,
            )
            finder.changeImplementationAddress(
                constants.OptimisticOracleV3,
                self._contracts["optimistic_oracle_v3"].address,
                sender=self.deployer,
            )

    def deploy_expanded_token_blueprint(self):
        if "expanded_token_blueprint" not in self._contracts:
            self._contracts["expanded_token_blueprint"] = self.deployer.declare(
                self.project.ExpandedERC20,
                "Expanded Token",
                "EXT",
                18
            )

    def deploy_outcome_token_factory(self):
        if "factory" not in self._contracts:
            blueprint = self._contracts["expanded_token_blueprint"]
            self._contracts["factory"] = self.deployer.deploy(
                self.project.OutComeTokenFactory,
                blueprint.contract_address,
            )
    
    def deploy_all(self):
        self.deploy_finder_contract()
        self.deploy_store_contract()
        self.deploy_ancillary_interface()
        self.deploy_currency()
        self.deploy_address_whitelist()
        self.deploy_identifier_whitelist()
        self.deploy_mock_oracle()
        self.register_contracts()
        self.deploy_optimistic_oracle_v3()
        self.deploy_expanded_token_blueprint()
        self.deploy_outcome_token_factory()
    
    def get_contracts(self):
        return self._contracts

    
    def deploy_prediction_market(self):
        if "prediction_market" not in self._contracts:

            self.deploy_all()

            finder = self._contracts["finder_contract"]
            whitelist = self._contracts["address_whitelist"]
            mock = self._contracts["mock_oracle"]
            currency = self._contracts["currency"]
            factory = self._contracts["factory"]
            optimistic_oracle_v3 = self._contracts["optimistic_oracle_v3"]
            self._contracts["prediction_market"] = self.deployer.deploy(
                self.project.PredictionMarket,
                finder.address,
                whitelist.address,
                optimistic_oracle_v3.address,
                mock.address,
                currency.address,
                factory.address,
            )
            factory.whitelist(self._contracts["prediction_market"].address, sender=self.deployer)
        return self._contracts["prediction_market"]

@pytest.fixture(scope="session")
def owner(accounts):
    return accounts[0]

@pytest.fixture(scope="session")
def user_wallet(accounts):
    return accounts[1]

@pytest.fixture(scope="session")
def asserter_wallet(accounts):
    return accounts[2]

@pytest.fixture(scope="session")
def other_account(accounts):
    return accounts[4]

@pytest.fixture(scope="session")
def sandbox(project, owner):
    return Sandbox(project, owner)