from django.db import models


class Enviroment(models.Model):
    """Enviroment Class on OneToMany with League models"""

    LEAGUE_GAME = [
        (1, 'SD 1001'),
        (2, 'DD 1001'),
        (3, 'SD 501'),
        (4, 'DD 501'),
        (5, 'SD 301'),
        (6, 'DD 301'),
        (7, 'SD 201'),
        (8, 'DD 201')
    ]

    WINNER_MATCH = [
        (1, 'Por Sets'),
        (2, 'Por Legs')
    ]

    meritPmin = models.IntegerField(default=80)
    meritAmin = models.IntegerField(default=70)
    meritBmin = models.IntegerField(default=60)
    meritCmin = models.IntegerField(default=50)
    meritDmin = models.IntegerField(default=40)
    meritRmin = models.IntegerField(default=30)
    meritTimeline = models.IntegerField(default=361)
    meritChampionBonus = models.IntegerField(default=150)
    meritSecondBonus = models.IntegerField(default=100)
    meritThirdBonus = models.IntegerField(default=50)
    meritDivAPoints = models.IntegerField(default=15)
    meritDivBPoints = models.IntegerField(default=9)
    meritDivCPoints = models.IntegerField(default=5)
    meritDivOthersPoints = models.IntegerField(default=3)
    matchWinPoints = models.IntegerField(default=3)
    matchDrawPoints = models.IntegerField(default=1)
    leagueMaxPlayers = models.IntegerField(default=16)
    leagueMinPlayers = models.IntegerField(default=8)
    allowAutoBye = models.IntegerField(default=3)
    allowAutoPromo = models.IntegerField(default=0)
    allowAutoDemo = models.IntegerField(default=0)
    leagueSubscriptionsEnds = models.IntegerField(default=31)
    leagueAplayoffs = models.BooleanField(default=False)
    leagueBplayoffs = models.BooleanField(default=False)
    leagueCplayoffs = models.BooleanField(default=False)
    leagueOthersplayoffs = models.BooleanField(default=False)
    leagueAMaxSet = models.IntegerField(default=1)
    leagueBMaxSet = models.IntegerField(default=1)
    leagueCMaxSet = models.IntegerField(default=1)
    leagueOthersMaxSet = models.IntegerField(default=1)
    leagueABestof = models.IntegerField(default=14)
    leagueBBestof = models.IntegerField(default=12)
    leagueCBestof = models.IntegerField(default=10)
    leagueOthersBestof = models.IntegerField(default=8)
    leagueAFirstTo = models.IntegerField(default=8)
    leagueBFirstTo = models.IntegerField(default=7)
    leagueCFirstTo = models.IntegerField(default=6)
    leagueOthersFirstTo = models.IntegerField(default=5)
    leagueAGameMode = models.IntegerField(choices=LEAGUE_GAME, default=3)
    leagueBGameMode = models.IntegerField(choices=LEAGUE_GAME, default=3)
    leagueCGameMode = models.IntegerField(choices=LEAGUE_GAME, default=3)
    leagueOthersGameMode = models.IntegerField(choices=LEAGUE_GAME, default=3)
    leagueAWinnerBy = models.IntegerField(choices=WINNER_MATCH, default=2)
    leagueBWinnerBy = models.IntegerField(choices=WINNER_MATCH, default=2)
    leagueCWinnerBy = models.IntegerField(choices=WINNER_MATCH, default=2)
    leagueOthersWinnerBy = models.IntegerField(choices=WINNER_MATCH, default=2)
    created_at = models.DateTimeField('Created at', auto_now_add=True)

    def retrieve(self):

        data = {'meritpoints': [0, self.meritDivAPoints, self.meritDivBPoints, self.meritDivCPoints, self.meritDivOthersPoints, self.meritDivOthersPoints, self.meritDivOthersPoints, self.meritDivOthersPoints, self.meritDivOthersPoints, self.meritDivOthersPoints, self.meritDivOthersPoints, self.meritDivOthersPoints],
               'leagueplayoffs': [0, self.leagueAplayoffs, self.leagueBplayoffs, self.leagueCplayoffs, self.leagueOthersplayoffs, self.leagueOthersplayoffs, self.leagueOthersplayoffs, self.leagueOthersplayoffs, self.leagueOthersplayoffs, self.leagueOthersplayoffs, self.leagueOthersplayoffs, self.leagueOthersplayoffs],
               'leaguemaxset': [0, self.leagueAMaxSet, self.leagueBMaxSet, self.leagueCMaxSet, self.leagueOthersMaxSet, self.leagueOthersMaxSet, self.leagueOthersMaxSet, self.leagueOthersMaxSet, self.leagueOthersMaxSet, self.leagueOthersMaxSet, self.leagueOthersMaxSet, self.leagueOthersMaxSet],
               'leaguebestof': [0, self.leagueABestof, self.leagueBBestof, self.leagueCBestof, self.leagueOthersBestof, self.leagueOthersBestof, self.leagueOthersBestof, self.leagueOthersBestof, self.leagueOthersBestof, self.leagueOthersBestof, self.leagueOthersBestof, self.leagueOthersBestof],
               'leaguefirstto': [0, self.leagueAFirstTo, self.leagueBFirstTo, self.leagueCFirstTo, self.leagueOthersFirstTo, self.leagueOthersFirstTo, self.leagueOthersFirstTo, self.leagueOthersFirstTo, self.leagueOthersFirstTo, self.leagueOthersFirstTo, self.leagueOthersFirstTo, self.leagueOthersFirstTo],
               'leaguegamemode': [0, self.leagueAGameMode, self.leagueBGameMode, self.leagueCGameMode, self.leagueOthersGameMode, self.leagueOthersGameMode, self.leagueOthersGameMode, self.leagueOthersGameMode, self.leagueOthersGameMode, self.leagueOthersGameMode, self.leagueOthersGameMode, self.leagueOthersGameMode],
               'leaguewinnerby': [0, self.leagueAWinnerBy, self.leagueBWinnerBy, self.leagueCWinnerBy, self.leagueOthersWinnerBy, self.leagueOthersWinnerBy, self.leagueOthersWinnerBy, self.leagueOthersWinnerBy, self.leagueOthersWinnerBy, self.leagueOthersWinnerBy, self.leagueOthersWinnerBy, self.leagueOthersWinnerBy]}

        return data



    class Meta:
        verbose_name_plural = "enviroments"
        verbose_name = "enviroment"
        ordering = ('-created_at',)
