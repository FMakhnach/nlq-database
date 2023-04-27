import pytest

import archie.app.brain as brain
from archie.models import Prompt


@pytest.mark.parametrize(
    'prompt', [
        'What is the day of week today?',
        'What was the last episode of Game of Thrones I\'ve watched',
        'how much did i spent last week',
        'Сколько раз я ходил в вуз за месяц?',
        'как назывался тот ресторан где я завтракал в Питере',
    ])
def test_is_question__question(prompt: str):
    prompt_obj = Prompt(prompt)
    is_question = brain.is_question(prompt_obj)
    assert is_question is True


@pytest.mark.parametrize(
    'prompt', [
        'I have a dinner with my parents today',
        'My weight is 71 kg',
        '2 games were lost, 1 was won',
        'Завтра мне нужно к врачу',
        '5/7 страниц переписаны',
    ])
def test_is_question__statement(prompt):
    prompt_obj = Prompt(prompt)
    is_question = brain.is_question(prompt_obj)
    assert is_question is False


@pytest.mark.parametrize(
    'prompt', [
        'List my appointments',
        'Give me overview of my reading this month',
        'Перечисли где я был на той неделе',
    ])
def test_is_question__request(prompt):
    prompt_obj = Prompt(prompt)
    is_question = brain.is_question(prompt_obj)
    assert is_question is True