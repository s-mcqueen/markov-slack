
import json
import re
import subprocess

USERS_JSON_FILE = '{}/users.json'
CHANNELS_JSON_FILE = '{}/channels.json'


def process_slack_export(slack_export_dir, bigram_file):
    handler = BiGramBuilder(slack_export_dir)
    handler.build_bigrams_in_memory()
    handler.export_bigrams(bigram_file)


# Note that a major weakness of this approach is that bigrams data must fit into memory
class BiGramBuilder(object):

    def __init__(self, slack_export_dir):
        self.bigrams = {}
        self.slack_export_dir = slack_export_dir
        self.users = self._parse_users(USERS_JSON_FILE.format(slack_export_dir))
        self.channels = self._parse_channels(CHANNELS_JSON_FILE.format(slack_export_dir))

    def build_bigrams_in_memory(self):
        # Find all json conversation files to parse
        all_files_to_parse = []
        for channel_name in self.channels:
            file_path = '{}/{}/'.format(self.slack_export_dir, channel_name)
            files = subprocess.check_output(['ls', file_path]).split('\n')
            files = ['{}{}'.format(file_path, f) for f in files if f]
            all_files_to_parse.extend(files)

        # Process each message individually and put it into an in-memory hash
        for file in all_files_to_parse:
            with open(file) as convo_json:
                convo_data = json.load(convo_json)
                convo_json.close()
                for message in convo_data:
                    self._process_message_dict(message)

    def export_bigrams(self, output_file):
        subprocess.call(['touch', output_file])
        with open(output_file, 'w') as output_file:
            json.dump(self.bigrams, output_file)

    def _process_message_dict(self, message):
        if not self._should_process_message_dict(message):
            return

        text = message['text']
        user_id = message['user']

        speaker = self.users[user_id]

        if speaker not in self.bigrams:
            self.bigrams[speaker] = {'\n':{}}

        words = re.findall(r'[^\s!,.?":;0-9]+', text)
        for i, word in enumerate(words):
            if i == 0:
                prev_word = '\n'
            else:
                prev_word = words[i-1]

            # add the bigram
            if word in self.bigrams[speaker][prev_word]:
                self.bigrams[speaker][prev_word][word] += 1
            else:
                self.bigrams[speaker][prev_word][word] = 1

            # add this word (so the prev_word check on the next word works)
            if word not in self.bigrams[speaker]:
                self.bigrams[speaker][word] = {}

            if word == words[-1]:
                if '\n' in self.bigrams[speaker][word]:
                    self.bigrams[speaker][word]['\n'] += 1
                else:
                    self.bigrams[speaker][word]['\n'] = 1

    def _should_process_message_dict(self, message):
        # We only care about messages that are of type "message" and
        # in the userset we care about
        return (message['type'] == 'message' and
                not message.get('subtype') and
                message['user'] in self.users)

    def _parse_users(self, json_file):
        users = {}
        with open(json_file) as users_json:
            users_data = json.load(users_json)
            users_json.close()
            for user in users_data:
                # We only care about humans
                if user['is_bot']:
                    continue
                users[user['id']] = user['name']

        return users

    def _parse_channels(self, json_file):
        channels = []
        with open(json_file) as channels_json:
            channels_data = json.load(channels_json)
            channels_json.close()
            for channel in channels_data:
                # We only care about unarchived channels
                if channel['is_archived']:
                    continue
                channels.append(channel['name'])

        return channels

