from archie.app.conversation import Conversation
from archie.models import ConversationId
from testcases import testcases

logger = print

def evaluate():
    scores = {}
    conversation = Conversation(ConversationId('0'))
    for i, testcase in enumerate(testcases):
        if 'enabled' in testcase and testcase['enabled'] is False:
            continue
        logger(f'(!) Running scenario #{i}: {testcase["title"]}.')
        scores[testcase['title']] = {}
        for case in testcase['subcases']:
            if 'enabled' in case and case['enabled'] is False:
                continue
            logger(f'> Running case "{case["title"]}"')
            scores[testcase['title']][case['title']] = {}
            for line in case['dialog']:
                if 'enabled' in line and line['enabled'] is False:
                    continue
                user_message = line["Q"]
                expected_response = line["A"]
                response = conversation.respond(line["Q"]).text
                logger(f'>> Q: {user_message}')
                logger(f'>> Expected: {expected_response}')
                logger(f'>> Got: {response}')
                logger(f'>> Score from 0 to 4: ', end='')
                score = int(input())
                scores[testcase['title']][case['title']][user_message] = score


if __name__ == "__main__":
    evaluate()
