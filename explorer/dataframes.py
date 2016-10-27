from core import utils
from explorer import models
from explorer.models import Championship, Match, Team, ResumeOdds, Table
from core.utils import Championships as champ
from core.utils import Path as path
import pandas as pd
from decimal import Decimal
from networkx.classes.function import is_empty


engine = models.getEngine()
session = models.getSession()

def listMatchesByChamp(champName):
    matches = session.query(Match.id, 
                            Match.championshipId,
                            Match.homeTeamId,
                            Match.awayTeamId,
                            Match.goalsHome,
                            Match.goalsAway,
                            Match.result,
                            Match.matchDate,
                            Match.roundNum,
                            Match.oddsHome,
                            Match.oddsDraw,
                            Match.oddsAway,
                            Championship.year, Championship.id).filter(Match.championshipId == Championship.id,
                                                      Championship.name == champName)
                  
    columns = ['ID','CHAMP','HT','AT','HG','AG','RSL','MDATE',\
                      'RD','HODD','DODD','AODD','YR']
    
    df = pd.DataFrame(data=matches.all(), columns=columns)
    
    df['TG'] = df['HG'] + df['AG']
    
    df.to_csv(path.NOTEBOOKS_DATA + champName + '-matches.csv',index=False);

     
'''
listMatches(champ.SPAIN_LA_LIGA[0])    
listMatches(champ.BRAZIL_SERIE_A[0])
listMatches(champ.BRAZIL_SERIE_B[0])
'''
    
def resumeMatchesByYear(typeOdds):

    championships = session.query(Championship).filter()

    gYears = []
    gChampionships = []
    gChampionshipId = []
    gMatches = []
    gMatchesOdds = []

    gResultHome = []
    gResultDraw = []
    gResultAway = []
    gResultFavorite = []
    gResultMedium = []
    gResultUnderdog = []

    gOddsHome = []
    gOddsDraw = []
    gOddsAway = []
    gOddsFavorite = []
    gOddsMedium = []
    gOddsUnderdog = []

    for champ in championships:

        matches = champ.listMatches()

        countMatches = 0
        countMatchesOdds = 0

        countResultHome = 0
        countResultDraw = 0
        countResultAway = 0
        countResultFavorite = 0
        countResultMedium = 0
        countResultUnderdog = 0

        sumOddsHome = Decimal(0)
        sumOddsDraw = Decimal(0)
        sumOddsAway = Decimal(0)
        sumOddsFavorite = Decimal(0)
        sumOddsMedium = Decimal(0)
        sumOddsUnderdog = Decimal(0)

        for match in matches:

            countMatches = countMatches + 1
            try:
                if (typeOdds == 'max'):
                    r = ResumeOdds.get(match.id)
                    match.oddsHome = r.maxHome
                    match.oddsDraw = r.maxDraw
                    match.oddsAway = r.maxAway

                if (match.result == Match.RESULT_HOME_WINNER):
                    countResultHome = countResultHome + 1
                    sumOddsHome = sumOddsHome + match.oddsHome
                elif (match.result == Match.RESULT_DRAW):
                    countResultDraw = countResultDraw + 1
                    sumOddsDraw = sumOddsDraw + match.oddsDraw
                else:
                    countResultAway = countResultAway + 1
                    sumOddsAway = sumOddsAway + match.oddsAway


                fma = match.result_fmu()
                if (fma == 'F'):
                    sumOddsFavorite = sumOddsFavorite + match.favorite_odd()
                    countResultFavorite = countResultFavorite + 1
                elif(fma == 'M'):
                    sumOddsMedium = sumOddsMedium + match.medium_odd()
                    countResultMedium = countResultMedium + 1
                else:
                    sumOddsUnderdog = sumOddsUnderdog + match.underdog_odd()
                    countResultUnderdog = countResultUnderdog + 1

                countMatchesOdds = countMatchesOdds + 1
            except:
                pass

        year = champ.year
        championshipName = champ.name
        championshipId = champ.id

        gYears.append(year)
        gChampionshipId.append(championshipId)
        gChampionships.append(championshipName)
        gMatches.append(countMatches)
        gMatchesOdds.append(countMatchesOdds)

        gResultHome.append(countResultHome)
        gResultDraw.append(countResultDraw)
        gResultAway.append(countResultAway)
        gResultFavorite.append(countResultFavorite)
        gResultMedium.append(countResultMedium)
        gResultUnderdog.append(countResultUnderdog)

        gOddsHome.append(sumOddsHome)
        gOddsDraw.append(sumOddsDraw)
        gOddsAway.append(sumOddsAway)
        gOddsFavorite.append(sumOddsFavorite)
        gOddsMedium.append(sumOddsMedium)
        gOddsUnderdog.append(sumOddsUnderdog)

    df = pd.DataFrame()

    df['YR'] = gYears
    df['CHAMP'] = gChampionships
    df['championship_id'] = gChampionshipId
    df['MP'] = gMatches
    df['MO'] = gMatchesOdds

    df['CH'] = gResultHome
    df['CD'] = gResultDraw
    df['CA'] = gResultAway
    df['CF'] = gResultFavorite
    df['CM'] = gResultMedium
    df['CU'] = gResultUnderdog

    df['SH'] = gOddsHome
    df['SD'] = gOddsDraw
    df['SA'] = gOddsAway
    df['SF'] = gOddsFavorite
    df['SM'] = gOddsMedium
    df['SU'] = gOddsUnderdog

    df['PLH'] = df['SH'] - df['MO']
    df['PLD'] = df['SD'] - df['MO']
    df['PLA'] = df['SA'] - df['MO']
    df['PLF'] = df['SF'] - df['MO']
    df['PLM'] = df['SM'] - df['MO']
    df['PLU'] = df['SU'] - df['MO']

    df['PCT_H'] = df['CH'] / df['MP']
    df['PCT_D'] = df['CD'] / df['MP']
    df['PCT_A'] = df['CA'] / df['MP']
    df['PCT_F'] = df['CF'] / df['MO']
    df['PCT_M'] = df['CM'] / df['MO']
    df['PCT_U'] = df['CU'] / df['MO']

    df.to_csv(path.NOTEBOOKS_DATA + 'resumeMatchesByYear_' + typeOdds + '.csv', index=False);


def listTables():

    df = pd.read_sql(session.query(Table).statement, session.bind)
   
    df['goals_difference'] = df['goals_for'] - df['goals_against']
    df['goals_difference_home'] = df['goals_for_home'] - df['goals_against_home']
    df['goals_difference_away'] = df['goals_for_away'] - df['goals_against_away']
    
    df.to_csv(path.NOTEBOOKS_DATA + 'tables.csv',index=False);
    
def listMatches():

    df = pd.read_sql(session.query(Match).statement, session.bind)
    
    df.to_csv(path.NOTEBOOKS_DATA + 'matches.csv',index=False);
    
def toForest():

    query = "select m.match_id as match_id, \
    m.championship_id as championship_id,\
    m.home_team_id as home_team_id, \
       m.away_team_id as away_team_id,\
       m.goals_home as goals_home,\
       m.goals_away as goals_away,\
       m.column_result as column_result,\
       m.odds_home as odd_home,\
       m.odds_draw as odd_draw,\
       m.odds_away as odd_away,\
       m.match_date as match_date,\
       m.round_num as round_num,\
       tbh.matches_played as h_matches_played,\
       tbh.winners as h_winners,\
       tbh.draws as h_draws,\
       tbh.loses as h_loses,\
       tbh.goals_for as h_goals_for,\
       tbh.goals_against as h_goals_against,\
       tbh.points as h_points,\
       tbh.matches_played_home as h_matches_played_home,\
       tbh.winners_home as h_winners_home,\
       tbh.draws_home as h_draws_home,\
       tbh.loses_home as h_loses_home,\
       tbh.goals_for_home as h_goals_for_home,\
       tbh.goals_against_home as h_goals_against_home,\
       tbh.points_home as h_points_home,\
       tbh.matches_played_away as h_matches_played_away,\
       tbh.winners_away as h_winners_away,\
       tbh.draws_away as h_draws_away,\
       tbh.loses_away as h_loses_away,\
       tbh.goals_for_away as h_goals_for_away,\
       tbh.goals_against_away as h_goals_against_away,\
       tbh.points_away as h_points_away,\
       tba.matches_played as a_matches_played,\
       tba.winners as a_winners,\
       tba.draws as a_draws,\
       tba.loses as a_loses,\
       tba.goals_for as a_goals_for,\
       tba.goals_against as a_goals_against,\
       tba.points as a_points,\
       tba.matches_played_home as a_matches_played_home,\
       tba.winners_home as a_winners_home,\
       tba.draws_home as a_draws_home,\
       tba.loses_home as a_loses_home,\
       tba.goals_for_home as a_goals_for_home,\
       tba.goals_against_home as a_goals_against_home,\
       tba.points_home as a_points_home,\
       tba.matches_played_away as a_matches_played_away,\
       tba.winners_away as a_winners_away,\
       tba.draws_away as a_draws_away,\
       tba.loses_away as a_loses_away,\
       tba.goals_for_away as a_goals_for_away,\
       tba.points_away as a_points_away\
    from (matches m INNER JOIN tables tbh ON \
    tbh.next_match_id = m.match_id and m.home_team_id = tbh.team_id) \
    INNER JOIN tables tba ON\
    (tba.next_match_id = m.match_id and m.away_team_id = tba.team_id) "

    print("a")
    df = pd.read_sql(query, session.bind)
    print(df)
    
    df.to_csv(path.NOTEBOOKS_DATA + 'matches-tables.csv',index=False);
                
  

toForest()

