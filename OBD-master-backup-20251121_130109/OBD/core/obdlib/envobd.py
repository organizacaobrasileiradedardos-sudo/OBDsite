

class EnviromentDefault:
    """
    This class is responsible for defaults values and other OBD Configs.
    """
    def __init__(self):
        self.meritPmin = 80
        self.meritAmin = 70
        self.meritBmin = 60
        self.meritCmin = 50
        self.meritDmin = 40
        self.meritRmin = 30
        self.meritTimeline = 361
        self.meritChampionBonus = 150
        self.meritSecondBonus = 100
        self.meritThirdBonus = 50
        self.meritDivAPoints = 15
        self.meritDivBPoints = 7
        self.meritDivCPoints = 3
        self.meritDivOthersPoints = 1
        self.matchWinPoints = 3
        self.matchDrawPoints = 1
        self.leagueMaxPlayers = 16
        self.leagueMinPlayers = 8
        self.allowAutoBye = 3
        self.allowAutoPromo = 0
        self.allowAutoDemo = 0
        self.leagueSubscriptionsEnds = 10
        self.leagueAMaxSet = 1
        self.leagueBMaxSet = 1
        self.leagueCMaxSet = 1
        self.leagueOthersMaxSet = 1
        self.leagueABestof = 14
        self.leagueBBestof = 12
        self.leagueCBestof = 10
        self.leagueOthersBestof = 8
        self.leagueAFirstTo = 8
        self.leagueBFirstTo = 7
        self.leagueCFirstTo = 6
        self.leagueOthersFirstTo = 5

    def __str__(self):
        return '(Default Value for Enviroment Model/Class -)'


class Hashes:
    pass
