import pytest
import utils

# utils.extract_phrase

def extract_phrase_test_base(text: str, expected: str):
    result = utils.extract_phrase(text)
    assert result == expected, f'Expected {expected}, got {result}'

@pytest.mark.parametrize('empty_string', ['', '    ', '  \n\r  '])
def test_extract_phrase_empty_string(empty_string: str):
    extract_phrase_test_base(text=empty_string, expected='')

def test_extract_phrase_single_word():
    extract_phrase_test_base(text=' \n phrase \r ', expected='phrase')

def test_extract_phrase_converts_to_lower():
    extract_phrase_test_base(text=' \n PhrAse \r ', expected='phrase')

def test_extract_phrase_multiple_words():
    extract_phrase_test_base(text=' \n Dentist Appointment \r ', expected='dentist appointment')

@pytest.mark.parametrize('text', ['hello', 'hello world', 'nothing to change'])
def test_extract_phrase_nothing_to_change(text):
    extract_phrase_test_base(text=text, expected=text)

# ===