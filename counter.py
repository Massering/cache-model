class Counter:
    tact: int
    hits: int
    attempts: int

    def __init__(self):
        self.tact = 0
        self.hits = 0
        self.attempts = 0

    def __iadd__(self, x: int):
        self.tact += x
        return self

    def hit(self):
        self.hits += 1
        self.attempts += 1

    def miss(self):
        self.attempts += 1

    def get_stat(self):
        if self.attempts == 0:
            return 0, self.tact
        return 100 * self.hits / self.attempts, self.tact
