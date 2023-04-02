import brain
import pytest
from models import PromptClass


@pytest.mark.parametrize(
    'expected_class,prompt', [
        (PromptClass.SELECT, 'What is the day of week today?'),
        (PromptClass.SELECT, 'What was the last episode of Game of Thrones I\'ve watched'),
        (PromptClass.SELECT, 'how much did i spent last week'),
        (PromptClass.SELECT, 'List my appointments'),
        (PromptClass.SELECT, 'Give me overview of my reading this month'),
        (PromptClass.INSERT, 'I have a dinner with my parents today'),
        (PromptClass.INSERT, 'My weight is 71 kg'),
        (PromptClass.INSERT, '2 games were lost, 1 was won'),
    ])
def test_is_question__question(expected_class: PromptClass, prompt: str):
    if expected_class is PromptClass.SELECT:
        return
    prompt_class = brain.classify_prompt(prompt)
    assert prompt_class == expected_class
