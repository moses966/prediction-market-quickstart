import  os
import sys
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from scripts import constants


@pytest.fixture(scope="session")
def deployer(accounts):
    yield accounts[0]

@pytest.fixture(scope="session")
def user_wallet(accounts):
    yield accounts[1]

@pytest.fixture(scope="session")
def asserter_wallet(accounts):
    yield accounts[2]

