import time


def getTimeStamp():
    return "[VOTING] [" + time.strftime('%Y-%m-%d %H:%M:%S') + "] "


def create_archived_votes():
    file = open("emojivotes.max", "r")
    raw = file.read()
    raw_voters = raw.split('\n')
    print(raw_voters)


class VotingListener:

    def __init__(self, emoji, thresh, client):
        print(getTimeStamp(), "Created Emoji Voter:", emoji.name)
        self.client = client
        self.threshold = thresh
        self.emoji = emoji
        self.active = True
        self.write_voter_to_file()

    # FORMAT OF WRITTEN FILES:
    # original submission message ID, channel ID of <- message, voting message id, channel ID of <- message
    def write_voter_to_file(self):
        file = open("emojivotes.max", "a")
        out = str(self.emoji.message.id) + "," + str(self.emoji.message.channel.id) + "," + str(
            self.emoji.voter_message.id) + "," + str(self.emoji.ann_channel.id) + '\n'
        print(out)
        file.write(out)
        file.close()

    def get_message_id(self):
        if self.active:
            s = self.emoji.get_voter_message()
            return s.id

    async def add_vote(self, reaction):
        channel = self.client.get_channel(reaction.channel_id)
        message = await channel.fetch_message(reaction.message_id)
        for reaction in message.reactions:
            if reaction.emoji.name == "posrep":
                print(getTimeStamp() + self.emoji.name, "Votes:", reaction.count)
                if reaction.count >= self.threshold:
                    return True, self.emoji.image.bytes, self.emoji.name, self.emoji.toBeReplaced
                else:
                    break
        return False, None, None, None

    def is_active(self):
        return self.emoji.in_use

    def destroy(self):
        self.active = False
