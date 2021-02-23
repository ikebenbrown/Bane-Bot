import time
from EmojiListener import EmojiListener


def getTimeStamp():
    return "[VOTING] [" + time.strftime('%Y-%m-%d %H:%M:%S') + "] "


async def create_archived_votes(client):
    file = open("emojivotes.max", "r")
    raw = file.read()
    raw_voters = raw.split('\n')
    out = []
    for voter in raw_voters:
        if voter != "":
            voter = voter.split(",")
            created_voter = await create_voter(voter, client)
            if created_voter is not None:
                out.append(created_voter)
    return out


async def create_voter(raw_voter, client):
    try:
        message_channel = await client.fetch_channel(int(raw_voter[1]))
        message = await message_channel.fetch_message(int(raw_voter[0]))

        announcements_channel = await client.fetch_channel(raw_voter[3])
        voter_message = await announcements_channel.fetch_message(raw_voter[2])

        emoji = EmojiListener(message, announcements_channel, message.guild, voter_message)
        await emoji.handle_image_silent()

        # TODO make this "15" automatically change the with the voting threshold
        return VotingListener(emoji, 15, client, False)

    except Exception:
        print(getTimeStamp(), "Failed to find message")
        return None


class VotingListener:

    def __init__(self, emoji, thresh, client, new_voter):
        self.client = client
        self.threshold = thresh
        self.emoji = emoji
        self.active = True
        if new_voter:
            self.write_voter_to_file()
            print(getTimeStamp() + "Created Emoji Voter:", emoji.name)
        else:
            print(getTimeStamp() + "Recovered Voter:", emoji.name)
    # FORMAT OF WRITTEN FILES:
    # original submission message ID, channel ID of <- message, voting message id, channel ID of <- message
    def write_voter_to_file(self):
        file = open("emojivotes.max", "a")
        out = str(self.emoji.message.id) + "," + str(self.emoji.message.channel.id) + "," + str(
            self.emoji.voter_message.id) + "," + str(self.emoji.ann_channel.id) + "," + str(time.time()) + "," \
              + str(self.emoji.message.author.id) + '\n'
        print(out)
        file.write(out)
        file.close()

    def get_message_id(self):
        if self.active:
            s = self.emoji.voter_message
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
