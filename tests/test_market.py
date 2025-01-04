import os
import sys
import ape
from ape import project
from hexbytes import HexBytes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from scripts import constants

def _decode_logs(receipt):
    decoded_logs = receipt.decode_logs()
    for log in decoded_logs:
        if log.event_name == "MarketInitialized":
            # extract the market_id
            _market_id = log.market_id

            # extract the outcome token addresses
            outcome_token_one = log.outcome1_token
            outcome_token_two = log.outcome2_token
            return _market_id, outcome_token_one, outcome_token_two


def test_market(
    owner,
    user_wallet,
    asserter_wallet,
    other_account,
    sandbox
):
    # deploy prediction market
    market = sandbox.deploy_prediction_market()

    # mint and appprove currency tokens
    sandbox.get_contracts()['currency'].allocateTo(owner, constants.reward, sender=owner)
    sandbox.get_contracts()['currency'].approve(market.address, constants.reward, sender=owner)

    # initialize market
    receipt = market.initialize_market(
        constants.outcome_one,
        constants.outcome_two,
        constants.description,
        constants.reward,
        constants.required_bond,
        sender=owner
    )
    assert sandbox.get_contracts()['currency'].balanceOf(market.address) == constants.reward
    logs = _decode_logs(receipt)
    assert logs[1] != constants.empty_address
    assert logs[1] == market.markets(HexBytes(logs[0])).outcome1_token

    # mint and appprove currency tokens
    sandbox.get_contracts()['currency'].allocateTo(owner, constants.reward, sender=owner)
    sandbox.get_contracts()['currency'].approve(market.address, constants.reward, sender=owner)
    with ape.reverts():
        market.initialize_market(
            constants.outcome_one,
            constants.outcome_one,
            constants.description,
            constants.reward,
            constants.required_bond,
            sender=owner
        )


    # mint and appprove currency tokens
    sandbox.get_contracts()["currency"].transfer(other_account, constants.reward, sender=owner)
    sandbox.get_contracts()['currency'].allocateTo(owner, constants.amount, sender=owner)
    sandbox.get_contracts()['currency'].approve(market.address, constants.amount, sender=owner)

    # create outcome tokens
    market.create_outcome_tokens(HexBytes(logs[0]), constants.amount, sender=owner)
    assert project.TestERC20.at((logs[1]), fetch_from_explorer=False).balanceOf(owner) == constants.amount
    assert project.TestERC20.at((logs[2]), fetch_from_explorer=False).balanceOf(owner) == constants.amount
    assert sandbox.get_contracts()['currency'].balanceOf(owner) == 0