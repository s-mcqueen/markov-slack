
import slack
import bigrams
import markov

# add a secrets.py file with SLACK_API_KEY and ICONS dict to run this code. Examples:
#
# SLACK_API_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
# ICONS = {
#     'username1': 'https://icon_url_1',
#     'username2': 'https://icon_url_2'
# }
#
import secrets

# Export your slack data ( https://my.slack.com/services/export) into a local directory
# and put the path in this var. "slack_export" is protected by .gitignore, so that's
# encouraged
SLACK_EXPORT_DIRECTORY = 'slack_export'

CHANNEL = 'general'             # Slack channel to send messages to
PERSON_TO_IMPERSONATE = 'user'  # put a name here from your own data

# The post-processed bigrams data. *.json will be ignored by git
BIGRAM_FILE = 'bigrams.json'

def run_once():
    # subsequent runs can just use post-processed bigrams file, so after
    # first run comment this out:
    bigrams.process_slack_export(SLACK_EXPORT_DIRECTORY, BIGRAM_FILE)

    icon_url = secrets.ICONS.get(PERSON_TO_IMPERSONATE)
    client = slack.Client(
        secrets.SLACK_API_KEY,
        CHANNEL,
        '{} {}'.format('markov', PERSON_TO_IMPERSONATE),
        icon_url=icon_url)

    speaker = markov.Speaker(BIGRAM_FILE, PERSON_TO_IMPERSONATE)
    client.post(speaker.probabilistic_sentence())


if __name__ == '__main__':
    run_once()
