
class Player:
    def __init__(self):
        raise NotImplementedError

    def play(self, scores):
        # use the scores so you can know when one team is scoring,
        # so you can figure out where you are vaguely if you have the flag, or vaguely where the flag is
        raise NotImplementedError

    def inform(self, message):
        raise NotImplementedError