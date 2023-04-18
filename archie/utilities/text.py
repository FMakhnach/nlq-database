def extract_phrase(text: str) -> str:
    start = 0
    end = len(text) - 1
    while start < len(text) - 1 and not text[start].isalnum():
        start += 1
    while end > 0 and not text[end].isalnum():
        end -= 1
    if start >= end:
        return ''
    return text[start:(end + 1)].lower()


def extract_json(text: str) -> str:
    first = text.find('{')
    last = text.rfind('}')
    if first == -1 or last == -1:
        raise Exception(f'Wrong json format: {text}')
    return text[first:(last+1)]
