import time


def getTimeStamp():
    return "[VOTING] [" + time.strftime('%Y-%m-%d %H:%M:%S') + "] "


class VotingListener:

    def __init__(self, emoji, thresh, client):
        print(getTimeStamp(), "Created Emoji Voter:", emoji.name)
        self.client = client
        self.threshold = thresh
        self.emoji = emoji
        self.active = True

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
