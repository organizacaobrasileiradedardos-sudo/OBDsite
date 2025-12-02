import random


class Fixturing:
    """
    This class is responsible for drawing tables and fixtures from OBD leagues.
    ...
    Attributes:
    -----------
    error: string
        Show messages about class instance actions.
    count: int
        Show the total number of matches.
    status: bool
        show the status of the instance. If False, not instanced yet or got error.
    matches: tuple
        All the combinations of matches between players.

    Methods:
    -----------
    __self__
        Start the SELF attributes.
    oneround(players)
        Return the single matches combinations given PLAYERS list.
    tworounds(players)
        Return the runoff matches combinations given PLAYERS list.
    randomize(self)
        Return a random new tuple of self.matches.
    spider(players) UNDER CONSTRUCTION
        Return the matches of SPIDER format gaming including byes and groups given PLAYERS lists.
    """

    def __init__(self):
        self.error = 'Draw not started'
        self.count = 0
        self.status = False
        self.matches = ()

    def __str__(self):
        return f'(fixture Class - Action: {self.error}; Matches: {self.count}; Status: {self.status})'

    def test_len(self, players):
        if len(players) < 2:
            self.error = 'Players have not the minimum amount'
            return False

    def oneround(self, players):

        if self.test_len(players) is False:
            return self.error

        self.error = 'Draw One started'
        for x in players:
            for y in range(len(players)):
                if x == players[y]:
                    pass

                else:
                    try:
                        self.matches.index((players[y], x))
                    except ValueError:
                        self.matches = self.matches + tuple({(x, players[y])})
                        self.count = self.count + 1
                    except TypeError:
                        self.error = 'Exeption: Another unknown error'
                        return self.error

        self.error = 'One Round fixture tables ware successfully generated'
        self.status = True
        return self.matches

    def tworounds(self, players):

        if self.test_len(players) is False:
            return self.error

        runoff = ()
        self.error = 'Draw Two started'
        self.oneround(players)

        for r in self.matches:
            runoff = runoff + tuple({(r[1], r[0])})
        self.matches = self.matches + runoff
        self.count = self.count * 2
        self.error = 'Runoff fixture tables ware successfully generated'
        return self.matches

    def randomize(self):
        self.matches = random.sample(self.matches, self.count)
        return self.matches

    def spider(self, players):
        pass
