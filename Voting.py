class VotingListener:

    def __init__(self, emoji):
        self.emoji = emoji
        self.votes = 0

    def get_message_id(self):
        s = self.emoji.get_voter_message()
        return s.id

    def add_vote(self, reaction):
        if reaction.emoji.name == "🐱":
            self.votes += 1
            print(self.emoji.name, "posreps =", self.votes)
        if self.votes > 0:
            return True, self.emoji.image.bytes, self.emoji.name

    def remove_vote(self, reaction):
        if reaction.emoji.name == "🐱":
            self.votes -= 1
            print(self.emoji.name, "posreps =", self.votes)
