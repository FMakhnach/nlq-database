import brain
import pytest


@pytest.mark.parametrize(
    'prompt', [
        'What is the day of week today?',
        'What was the last episode of Game of Thrones I\'ve watched',
        'how much did i spent last week'
    ])
def test_is_question__question(prompt: str):
    is_question = brain.is_question(prompt)
    assert is_question is True


@pytest.mark.parametrize(
    'prompt', [
        'I have a dinner with my parents today',
        'My weight is 71 kg',
        '2 games were lost, 1 was won'
    ])
def test_is_question__statement(prompt):
    is_question = brain.is_question(prompt)
    assert is_question is False


@pytest.mark.parametrize(
    'prompt', [
        'List my appointments',
        'Give me overview of my reading this month',
    ])
def test_is_question__request(prompt):
    is_question = brain.is_question(prompt)
    assert is_question is True