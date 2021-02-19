class VotingListener:

    def __init__(self, emoji, thresh):
        self.threshold = thresh
        self.emoji = emoji
        self.votes = 0
        self.active = True

    def get_message_id(self):
        if self.active:
            s = self.emoji.get_voter_message()
            return s.id

    def add_vote(self, reaction):
        if self.active:
            if reaction.emoji.name == "posrep":
                self.votes += 1
                print(self.emoji.name, "posreps =", self.votes)
            if self.votes >= self.threshold:
                return True, self.emoji.image.bytes, self.emoji.name, self.emoji.toBeReplaced
            else:
                return False, None, None, None
        else:
            return False, None, None, None

    def remove_vote(self, reaction):
        if self.active:
            if reaction.emoji.name == "posrep":
                self.votes -= 1
                print(self.emoji.name, "posreps =", self.votes)

    def is_active(self):
        return self.emoji.in_use

    def destroy(self):
        self.active = False
