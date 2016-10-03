'''
Created on 30 de set de 2016

@author: igormago
'''
import unittest
from explorer.models import Ranking, Bookmaker, Championship, Match, Odds, Team
from explorer.models import OddsAH, OddsBTS, OddsDC, OddsDNB, OddsOU, ResumeOdds
from explorer.models import ResumeOddsAH, ResumeOddsOU, session
from datetime import date
from decimal import Decimal

class RankingTest(unittest.TestCase):


    def assertRanking(self, ranking, matchId, teamId,local, matchesPlayed, lastMatchesNum, winners, draws, loses, goalsScored,\
                      goalsConceded, points):

        self.assertEqual(ranking.matchId,matchId)
        self.assertEqual(ranking.teamId,teamId)
        self.assertEqual(ranking.local,local)
        self.assertEqual(ranking.matchesPlayed,matchesPlayed)
        self.assertEqual(ranking.lastMatchesNum,lastMatchesNum)
        self.assertEqual(ranking.winners,winners)
        self.assertEqual(ranking.draws,draws)
        self.assertEqual(ranking.loses,loses)
        self.assertEqual(ranking.goalsFor,goalsScored)
        self.assertEqual(ranking.goalsAgainst,goalsConceded)


    def testRanking(self):

        rankings = session.query(Ranking).filter(Ranking.matchId == 'pfykXqR9')

        rankingsTotal = rankings.filter(Ranking.local == 'B')
        self.assertEqual(rankingsTotal.count(),20)

        rankingsHome = rankings.filter(Ranking.local == 'H')
        self.assertEqual(rankingsHome.count(),5)

        rankingsAway = rankings.filter(Ranking.local == 'A')
        self.assertEqual(rankingsAway.count(),6)

        corinthians = session.query(Team).filter(Team.name == 'Corinthians').one()
        pontePreta = session.query(Team).filter(Team.name == 'Ponte Preta').one()

        rankCorinthians = rankingsTotal.filter(Ranking.teamId == corinthians.id)

        r = rankCorinthians.filter(Ranking.lastMatchesNum == 1).one()
        RankingTest.assertRanking(self,r,'pfykXqR9',corinthians.id,'B',9,1,1,0,0,2,1,3)
        r = rankCorinthians.filter(Ranking.lastMatchesNum == 2).one()
        RankingTest.assertRanking(self,r,'pfykXqR9',corinthians.id,'B',9,2,1,0,1,2,2,3)
        r = rankCorinthians.filter(Ranking.lastMatchesNum == 3).one()
        RankingTest.assertRanking(self,r,'pfykXqR9',corinthians.id,'B',9,3,2,0,1,4,3,6)
        r = rankCorinthians.filter(Ranking.lastMatchesNum == 4).one()
        RankingTest.assertRanking(self,r,'pfykXqR9',corinthians.id,'B',9,4,3,0,1,5,3,9)
        r = rankCorinthians.filter(Ranking.lastMatchesNum == 5).one()
        RankingTest.assertRanking(self,r,'pfykXqR9',corinthians.id,'B',9,5,3,0,2,6,6,9)
        r = rankCorinthians.filter(Ranking.lastMatchesNum == 6).one()
        RankingTest.assertRanking(self,r,'pfykXqR9',corinthians.id,'B',9,6,3,0,3,6,8,9)
        r = rankCorinthians.filter(Ranking.lastMatchesNum == 7).one()
        RankingTest.assertRanking(self,r,'pfykXqR9',corinthians.id,'B',9,7,3,1,3,6,8,10)
        r = rankCorinthians.filter(Ranking.lastMatchesNum == 8).one()
        RankingTest.assertRanking(self,r,'pfykXqR9',corinthians.id,'B',9,8,4,1,3,7,8,13)
        r = rankCorinthians.filter(Ranking.lastMatchesNum == 9).one()
        RankingTest.assertRanking(self,r,'pfykXqR9',corinthians.id,'B',9,9,5,1,3,8,8,16)

        r = rankCorinthians.filter(Ranking.lastMatchesNum == 10)
        self.assertEqual(r.count(),0)

        r = rankCorinthians.filter(Ranking.lastMatchesNum == 0)
        self.assertEqual(r.count(),1)

        rankPontePreta = rankingsTotal.filter(Ranking.teamId == pontePreta.id)
        r = rankPontePreta.filter(Ranking.lastMatchesNum == 1).one()
        RankingTest.assertRanking(self,r,'pfykXqR9',pontePreta.id,'B',9,1,1,0,0,2,1,3)
        r = rankPontePreta.filter(Ranking.lastMatchesNum == 2).one()
        RankingTest.assertRanking(self,r,'pfykXqR9',pontePreta.id,'B',9,2,1,0,1,2,3,3)
        r = rankPontePreta.filter(Ranking.lastMatchesNum == 3).one()
        RankingTest.assertRanking(self,r,'pfykXqR9',pontePreta.id,'B',9,3,1,1,1,2,3,4)
        r = rankPontePreta.filter(Ranking.lastMatchesNum == 4).one()
        RankingTest.assertRanking(self,r,'pfykXqR9',pontePreta.id,'B',9,4,1,2,1,4,5,5)
        r = rankPontePreta.filter(Ranking.lastMatchesNum == 5).one()
        RankingTest.assertRanking(self,r,'pfykXqR9',pontePreta.id,'B',9,5,2,2,1,7,5,8)
        r = rankPontePreta.filter(Ranking.lastMatchesNum == 6).one()
        RankingTest.assertRanking(self,r,'pfykXqR9',pontePreta.id,'B',9,6,3,2,1,10,6,11)
        r = rankPontePreta.filter(Ranking.lastMatchesNum == 7).one()
        RankingTest.assertRanking(self,r,'pfykXqR9',pontePreta.id,'B',9,7,3,3,1,11,7,12)
        r = rankPontePreta.filter(Ranking.lastMatchesNum == 8).one()
        RankingTest.assertRanking(self,r,'pfykXqR9',pontePreta.id,'B',9,8,4,3,1,12,7,15)
        r = rankPontePreta.filter(Ranking.lastMatchesNum == 9).one()
        RankingTest.assertRanking(self,r,'pfykXqR9',pontePreta.id,'B',9,9,4,4,1,15,10,16)

        #Ranking home
        r = rankPontePreta.filter(Ranking.lastMatchesNum == 10)
        self.assertEqual(r.count(),0)

        r = rankPontePreta.filter(Ranking.lastMatchesNum == 0)
        self.assertEqual(r.count(),1)

        r = rankingsHome.filter(Ranking.lastMatchesNum == 1).one()
        RankingTest.assertRanking(self,r,'pfykXqR9',corinthians.id,'H',4,1,1,0,0,2,1,3)

        r = rankingsHome.filter(Ranking.lastMatchesNum == 2).one()
        RankingTest.assertRanking(self,r,'pfykXqR9',corinthians.id,'H',4,2,2,0,0,4,2,6)

        r = rankingsHome.filter(Ranking.lastMatchesNum == 3).one()
        RankingTest.assertRanking(self,r,'pfykXqR9',corinthians.id,'H',4,3,2,0,1,4,4,6)

        r = rankingsHome.filter(Ranking.lastMatchesNum == 4).one()
        RankingTest.assertRanking(self,r,'pfykXqR9',corinthians.id,'H',4,4,3,0,1,5,4,9)

        r = rankingsHome.filter(Ranking.lastMatchesNum == 5)
        self.assertEqual(r.count(),0)

        r = rankingsHome.filter(Ranking.lastMatchesNum == 0)
        self.assertEqual(r.count(),1)

        #Ranking away
        r = rankingsAway.filter(Ranking.lastMatchesNum == 1).one()
        RankingTest.assertRanking(self,r,'pfykXqR9',pontePreta.id,'A',5,1,0,0,1,0,2,0)

        r = rankingsAway.filter(Ranking.lastMatchesNum == 2).one()
        RankingTest.assertRanking(self,r,'pfykXqR9',pontePreta.id,'A',5,2,0,1,1,2,4,1)

        r = rankingsAway.filter(Ranking.lastMatchesNum == 3).one()
        RankingTest.assertRanking(self,r,'pfykXqR9',pontePreta.id,'A',5,3,1,1,1,5,4,4)

        r = rankingsAway.filter(Ranking.lastMatchesNum == 4).one()
        RankingTest.assertRanking(self,r,'pfykXqR9',pontePreta.id,'A',5,4,1,2,1,6,5,5)

        r = rankingsAway.filter(Ranking.lastMatchesNum == 5).one()
        RankingTest.assertRanking(self,r,'pfykXqR9',pontePreta.id,'A',5,5,1,3,1,9,8,6)

        r = rankingsAway.filter(Ranking.lastMatchesNum == 6)
        self.assertEqual(r.count(),0)

        r = rankingsAway.filter(Ranking.lastMatchesNum == 0)
        self.assertEqual(r.count(),1)


    def testMatch(self):

        match = session.query(Match).filter(Match.id == 'pfykXqR9').one()

        corinthians = session.query(Team).filter(Team.name == 'Corinthians').one()
        pontePreta = session.query(Team).filter(Team.name == 'Ponte Preta').one()

        championship = session.query(Championship).filter(Championship.name == 'serie-a-2015').one()

        self.assertEqual(match.id,'pfykXqR9')
        self.assertEqual(match.homeTeamId,corinthians.id)
        self.assertEqual(match.awayTeamId,pontePreta.id)
        self.assertEqual(match.championshipId,championship.id)
        self.assertEqual(match.goalsHome,2)
        self.assertEqual(match.goalsAway,0)
        self.assertEqual(match.oddsHome,Decimal('1.75'))
        self.assertEqual(match.oddsDraw,Decimal('3.35'))
        self.assertEqual(match.oddsAway,Decimal('4.74'))
        self.assertEqual(match.round, 10)
        self.assertEqual(match.matchDate,date(2015,7,3))

    def testChampionship(self):

        championship = session.query(Championship).filter(Championship.name == 'serie-a-2015').one()

        self.assertEqual(championship.name,'serie-a-2015')
        self.assertEqual(championship.year,2015)




class OddsTest(unittest.TestCase):

    def assertOdds(self, matchId):
        bookmaker = Bookmaker.get('10Bet')
        odd = Odds.get(matchId=matchId, bookmakerId=bookmaker.id)
        self.assertEqual(odd.oddsHome, Decimal('1.63'))
        self.assertEqual(odd.oddsDraw, Decimal('3.50'))
        self.assertEqual(odd.oddsAway, Decimal('5.35'))
        bookmaker = Bookmaker.get('youwin')
        odd = Odds.get(matchId=matchId, bookmakerId=bookmaker.id)
        self.assertEqual(odd.oddsHome, Decimal('1.64'))
        self.assertEqual(odd.oddsDraw, Decimal('3.39'))
        self.assertEqual(odd.oddsAway, Decimal('5.10'))

    def assertOddsOU(self, matchId):

        bookmaker = Bookmaker.get('youwin')
        odd = OddsOU.get(matchId=matchId, bookmakerId=bookmaker.id, goals=0.5)
        self.assertEqual(odd.oddsOver, Decimal('1.07'))
        self.assertEqual(odd.oddsUnder, Decimal('6.52'))
        odd = OddsOU.get(matchId=matchId, bookmakerId=bookmaker.id, goals=1.5)
        self.assertEqual(odd.oddsOver, Decimal('1.37'))
        self.assertEqual(odd.oddsUnder, Decimal('2.76'))

        bookmaker = Bookmaker.get('10Bet')
        odd = OddsOU.get(matchId=matchId, bookmakerId=bookmaker.id, goals=1.75)
        self.assertEqual(odd.oddsOver, Decimal('1.47'))
        self.assertEqual(odd.oddsUnder, Decimal('2.45'))
        odd = OddsOU.get(matchId=matchId, bookmakerId=bookmaker.id, goals=2.00)
        self.assertEqual(odd.oddsOver, Decimal('1.71'))
        self.assertEqual(odd.oddsUnder, Decimal('2.14'))

        bookmaker = Bookmaker.get('Pinnacle')
        odd = OddsOU.get(matchId=matchId, bookmakerId=bookmaker.id, goals=2.00)
        self.assertEqual(odd.oddsOver, Decimal('1.75'))
        self.assertEqual(odd.oddsUnder, Decimal('2.18'))

        odd = OddsOU.get(matchId=matchId, bookmakerId=bookmaker.id, goals=2.25)
        self.assertEqual(odd.oddsOver, Decimal('2.06'))
        self.assertEqual(odd.oddsUnder, Decimal('1.84'))

        odd = OddsOU.get(matchId=matchId, bookmakerId=bookmaker.id, goals=2.50)
        self.assertEqual(odd.oddsOver, Decimal('2.36'))
        self.assertEqual(odd.oddsUnder, Decimal('1.64'))

        odd = OddsOU.get(matchId=matchId, bookmakerId=bookmaker.id, goals=2.75)
        self.assertEqual(odd.oddsOver, Decimal('2.82'))
        self.assertEqual(odd.oddsUnder, Decimal('1.45'))

        bookmaker = Bookmaker.get('Paddy Power')
        odd = OddsOU.get(matchId=matchId, bookmakerId=bookmaker.id, goals=3.50)
        self.assertEqual(odd.oddsOver, Decimal('4.00'))
        self.assertEqual(odd.oddsUnder, Decimal('1.2'))

        odd = OddsOU.get(matchId=matchId, bookmakerId=bookmaker.id, goals=4.50)
        self.assertEqual(odd.oddsOver, Decimal('7.50'))
        self.assertEqual(odd.oddsUnder, Decimal('1.06'))

        bookmaker = Bookmaker.get('bet-at-home')
        odd = OddsOU.get(matchId=matchId, bookmakerId=bookmaker.id, goals=5.50)
        self.assertEqual(odd.oddsOver, Decimal('19.76'))
        self.assertEqual(odd.oddsUnder, Decimal('1.01'))

        bookmaker = Bookmaker.get('youwin')
        odd = OddsOU.get(matchId=matchId, bookmakerId=bookmaker.id, goals=5.50)
        self.assertEqual(odd.oddsOver, Decimal('10.26'))
        self.assertEqual(odd.oddsUnder, Decimal('1.01'))


    def assertOddsAH(self,matchId):

        bookmaker = Bookmaker.get('bet365')
        odd = OddsAH.get(matchId=matchId, bookmakerId=bookmaker.id, handicap='-2.5, -3')
        self.assertEqual(odd.oddsHome, Decimal('7.80'))
        self.assertEqual(odd.oddsAway, Decimal('1.09'))

        odd = OddsAH.get(matchId=matchId, bookmakerId=bookmaker.id, handicap='-2.5')
        self.assertEqual(odd.oddsHome, Decimal('6.40'))
        self.assertEqual(odd.oddsAway, Decimal('1.12'))

        odd = OddsAH.get(matchId=matchId, bookmakerId=bookmaker.id, handicap='-2, -2.5')
        self.assertEqual(odd.oddsHome, Decimal('6.00'))
        self.assertEqual(odd.oddsAway, Decimal('1.13'))

        odd = OddsAH.get(matchId=matchId, bookmakerId=bookmaker.id, handicap='-1.5, -2')
        self.assertEqual(odd.oddsHome, Decimal('3.70'))
        self.assertEqual(odd.oddsAway, Decimal('1.26'))

        odd = OddsAH.get(matchId=matchId, bookmakerId=bookmaker.id, handicap='-1.5')
        self.assertEqual(odd.oddsHome, Decimal('3.00'))
        self.assertEqual(odd.oddsAway, Decimal('1.38'))

        odd = OddsAH.get(matchId=matchId, bookmakerId=bookmaker.id, handicap='-1, -1.5')
        self.assertEqual(odd.oddsHome, Decimal('2.60'))
        self.assertEqual(odd.oddsAway, Decimal('1.48'))

        odd = OddsAH.get(matchId=matchId, bookmakerId=bookmaker.id, handicap='-1')
        self.assertEqual(odd.oddsHome, Decimal('2.25'))
        self.assertEqual(odd.oddsAway, Decimal('1.63'))

        odd = OddsAH.get(matchId=matchId, bookmakerId=bookmaker.id, handicap='-0.5, -1')
        self.assertEqual(odd.oddsHome, Decimal('1.90'))
        self.assertEqual(odd.oddsAway, Decimal('1.95'))

        odd = OddsAH.get(matchId=matchId, bookmakerId=bookmaker.id, handicap='-0.5')
        self.assertEqual(odd.oddsHome, Decimal('1.68'))
        self.assertEqual(odd.oddsAway, Decimal('2.15'))

        odd = OddsAH.get(matchId=matchId, bookmakerId=bookmaker.id, handicap='0, -0.5')
        self.assertEqual(odd.oddsHome, Decimal('1.45'))
        self.assertEqual(odd.oddsAway, Decimal('2.67'))

        odd = OddsAH.get(matchId=matchId, bookmakerId=bookmaker.id, handicap='0')
        self.assertEqual(odd.oddsHome, Decimal('1.24'))
        self.assertEqual(odd.oddsAway, Decimal('3.90'))

        odd = OddsAH.get(matchId=matchId, bookmakerId=bookmaker.id, handicap='0, 0.5')
        self.assertEqual(odd.oddsHome, Decimal('1.19'))
        self.assertEqual(odd.oddsAway, Decimal('4.50'))

        odd = OddsAH.get(matchId=matchId, bookmakerId=bookmaker.id, handicap='+0.5')
        self.assertEqual(odd.oddsHome, Decimal('1.16'))
        self.assertEqual(odd.oddsAway, Decimal('5.25'))

        odd = OddsAH.get(matchId=matchId, bookmakerId=bookmaker.id, handicap='0.5, 1')
        self.assertEqual(odd.oddsHome, Decimal('1.10'))
        self.assertEqual(odd.oddsAway, Decimal('7.20'))

    def assertOddsDNB(self,matchId):

        bookmaker = Bookmaker.get('888sport')
        odd = OddsDNB.get(matchId=matchId, bookmakerId=bookmaker.id)
        self.assertEqual(odd.oddsHome, Decimal('1.20'))
        self.assertEqual(odd.oddsAway, Decimal('4.00'))

        bookmaker = Bookmaker.get('BetVictor')
        odd = OddsDNB.get(matchId=matchId, bookmakerId=bookmaker.id)
        self.assertEqual(odd.oddsHome, Decimal('1.25'))
        self.assertEqual(odd.oddsAway, Decimal('4.00'))

        bookmaker = Bookmaker.get('youwin')
        odd = OddsDNB.get(matchId=matchId, bookmakerId=bookmaker.id)
        self.assertEqual(odd.oddsHome, Decimal('1.23'))
        self.assertEqual(odd.oddsAway, Decimal('3.51'))

    def assertOddsDC(self,matchId):

        bookmaker = Bookmaker.get('10Bet')
        odd = OddsDC.get(matchId=matchId, bookmakerId=bookmaker.id)
        self.assertEqual(odd.oddsHomeDraw, Decimal('1.13'))
        self.assertEqual(odd.oddsHomeAway, Decimal('1.24'))
        self.assertEqual(odd.oddsAwayDraw, Decimal('2.10'))

        bookmaker = Bookmaker.get('bwin')
        odd = OddsDC.get(matchId=matchId, bookmakerId=bookmaker.id)
        self.assertEqual(odd.oddsHomeDraw, Decimal('1.12'))
        self.assertEqual(odd.oddsHomeAway, Decimal('1.22'))
        self.assertEqual(odd.oddsAwayDraw, Decimal('2.20'))

        bookmaker = Bookmaker.get('youwin')
        odd = OddsDC.get(matchId=matchId, bookmakerId=bookmaker.id)
        self.assertEqual(odd.oddsHomeDraw, Decimal('1.15'))
        self.assertEqual(odd.oddsHomeAway, Decimal('1.24'))
        self.assertEqual(odd.oddsAwayDraw, Decimal('1.91'))

    def assertOddsBTS(self,matchId):

        bookmaker = Bookmaker.get('10Bet')
        odd = OddsBTS.get(matchId=matchId, bookmakerId=bookmaker.id)
        self.assertEqual(odd.oddsYes, Decimal('2.20'))
        self.assertEqual(odd.oddsNo, Decimal('1.59'))

        bookmaker = Bookmaker.get('bwin')
        odd = OddsBTS.get(matchId=matchId, bookmakerId=bookmaker.id)
        self.assertEqual(odd.oddsYes, Decimal('2.05'))
        self.assertEqual(odd.oddsNo, Decimal('1.70'))

        bookmaker = Bookmaker.get('youwin')
        odd = OddsBTS.get(matchId=matchId, bookmakerId=bookmaker.id)
        self.assertEqual(odd.oddsYes, Decimal('2.11'))
        self.assertEqual(odd.oddsNo, Decimal('1.62'))

    def testOdds(self):

        matchId = 'EcaXPn1g'
        odds = Odds.list(matchId)
        oddsOU = OddsOU.list(matchId)
        oddsAH = OddsAH.list(matchId)
        oddsDC = OddsDC.list(matchId)
        oddsDNB = OddsDNB.list(matchId)
        oddsBTS = OddsBTS.list(matchId)

        self.assertEqual(len(odds),25)
        self.assertEqual(len(oddsOU),108)
        self.assertEqual(len(oddsAH),45)
        self.assertEqual(len(oddsDC),18)
        self.assertEqual(len(oddsDNB),10)
        self.assertEqual(len(oddsBTS),14)

        self.assertOdds(matchId)
        self.assertOddsOU(matchId)
        self.assertOddsAH(matchId)
        self.assertOddsDNB(matchId)
        self.assertOddsDC(matchId)
        self.assertOddsBTS(matchId)


    def testResumes(self):

        #Seria A 2015 - Atletico x Chapecoense (Round 38)
        matchId = 'OEZc7upD'

        odd = ResumeOdds.get(matchId)

        self.assertEqual(round(odd.avgHome,2), Decimal('1.29'))
        self.assertEqual(round(odd.avgDraw,2), Decimal('5.06'))
        self.assertEqual(odd.avgAway, Decimal('9.63'))
        self.assertEqual(odd.maxHome, Decimal('1.31'))
        self.assertEqual(odd.maxDraw, Decimal('5.67'))
        self.assertEqual(odd.maxAway, Decimal('12.06'))
        self.assertEqual(odd.minHome, Decimal('1.25'))
        self.assertEqual(odd.minDraw, Decimal('4.75'))
        self.assertEqual(odd.minAway, Decimal('8.00'))
        self.assertEqual(odd.count, 25)

        assertions = [
                [Decimal('0.5'),Decimal('1.03'),Decimal('11.66'),
                 Decimal('1.04'),Decimal('13.37'),Decimal('1.01'),Decimal('8'),Decimal('13')]
        ]

        for a in assertions:

            odd = ResumeOddsOU().get(matchId, a[0])
            self.assertEqual(odd.avgOver,a[1])
            self.assertEqual(odd.avgUnder,a[2])
            self.assertEqual(odd.maxOver,a[3])
            self.assertEqual(odd.maxUnder,(a[4]))
            self.assertEqual(odd.minOver,a[5])
            self.assertEqual(odd.minUnder,a[6])
            self.assertEqual(odd.count,a[7])

        odds = ResumeOddsOU().listByMatch(matchId=matchId)
        self.assertEqual(len(odds),12)

        assertions = [
                ['-1.5, -2',Decimal('2.14'),Decimal('1.74'),
                 Decimal('2.16'),Decimal('1.78'),Decimal('2.08'),Decimal('1.68'),Decimal('4')]
        ]

        for a in assertions:

            odd = ResumeOddsAH().get(matchId, a[0])
            self.assertEqual(odd.avgHome,a[1])
            self.assertEqual(odd.avgAway,a[2])
            self.assertEqual(odd.maxHome,a[3])
            self.assertEqual(odd.maxAway,(a[4]))
            self.assertEqual(odd.minHome,a[5])
            self.assertEqual(odd.minAway,a[6])
            self.assertEqual(odd.count,a[7])

        odds = ResumeOddsAH().listByMatch(matchId=matchId)
        self.assertEqual(len(odds),14)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()