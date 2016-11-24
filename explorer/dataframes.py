from decimal import Decimal

from astropy.io.votable import tablewriter
from networkx.classes.function import is_empty
from sklearn import cross_validation
from sklearn.ensemble.forest import RandomForestClassifier
from sqlalchemy.orm import joinedload, aliased
from sqlalchemy.sql.expression import or_, and_

from core import utils
from core.utils import Championships as champ
from core.utils import Path as path
from explorer import models
from explorer.models import Championship, Match, Team, ResumeOdds, Table
import pandas as pd


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
                            Match.oddHome,
                            Match.oddDraw,
                            Match.oddAway,
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
                    match.oddHome = r.maxHome
                    match.oddDraw = r.maxDraw
                    match.oddAway = r.maxAway

                if (match.result == Match.RESULT_HOME_WINNER):
                    countResultHome = countResultHome + 1
                    sumOddsHome = sumOddsHome + match.oddHome
                elif (match.result == Match.RESULT_DRAW):
                    countResultDraw = countResultDraw + 1
                    sumOddsDraw = sumOddsDraw + match.oddDraw
                else:
                    countResultAway = countResultAway + 1
                    sumOddsAway = sumOddsAway + match.oddAway


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

    query = "select m.match_id as match_id,\
        m.championship_id as championship_id,\
        m.home_team_id as home_team_id, \
        m.away_team_id as away_team_id,\
        m.goals_home as goals_home,\
        m.goals_away as goals_away,\
        m.column_result as column_result,\
        m.odd_home as odd_home,\
        m.odd_draw as odd_draw,\
        m.odd_away as odd_away,\
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
       tba.goals_against_away as a_goals_against_away,\
       tba.points_away as a_points_away, \
       LEAST (m.odd_home, m.odd_draw, m.odd_away) as odd_favorite, \
       GREATEST (m.odd_home, m.odd_draw, m.odd_away) as odd_underdog \
    from (matches m INNER JOIN tables tbh ON \
    tbh.next_match_id = m.match_id and m.home_team_id = tbh.team_id) \
    INNER JOIN tables tba ON\
    (tba.next_match_id = m.match_id and m.away_team_id = tba.team_id) "

    df = pd.read_sql(query, session.bind)
    
    df['h_winners_mean'] = round(df['h_winners'] / df['h_matches_played'],2)
    df['h_draws_mean'] = round(df['h_draws'] / df['h_matches_played'],2)
    df['h_loses_mean'] = round(df['h_loses'] / df['h_matches_played'],2)
    df['h_goals_for_mean'] = round(df['h_goals_for'] / df['h_matches_played'],2)
    df['h_goals_against_mean'] = round(df['h_goals_against'] / df['h_matches_played'],2)
    df['h_points_mean'] = round(df['h_points'] / df['h_matches_played'],2)
    
    df['h_winners_home_mean'] = round(df['h_winners_home'] / df['h_matches_played_home'],2)
    df['h_draws_home_mean'] =  round(df['h_draws_home'] / df['h_matches_played_home'],2)
    df['h_loses_home_mean'] =  round(df['h_loses_home'] / df['h_matches_played_home'],2)
    df['h_goals_for_home_mean'] =  round(df['h_goals_for_home'] / df['h_matches_played_home'],2)
    df['h_goals_against_home_mean'] = round(df['h_goals_against_home'] / df['h_matches_played_home'],2)
    df['h_points_home_mean'] = round(df['h_points_home'] / df['h_matches_played_home'],2)
    
    df['h_winners_away_mean'] = round(df['h_winners_away'] / df['h_matches_played_away'],2)        
    df['h_draws_away_mean'] = round(df['h_draws_away'] / df['h_matches_played_away'],2)        
    df['h_loses_away_mean'] = round(df['h_loses_away'] / df['h_matches_played_away'],2)    
    df['h_goals_for_away_mean'] = round(df['h_goals_for_away'] / df['h_matches_played_away'],2)    
    df['h_goals_against_away_mean'] = round(df['h_goals_against_away'] / df['h_matches_played_away'],2)    
    df['h_points_away_mean'] = round(df['h_points_away'] / df['h_matches_played_away'],2)            
    
    df['a_winners_mean'] = round(df['a_winners'] / df['a_matches_played'],2)
    df['a_draws_mean'] = round(df['a_draws'] / df['a_matches_played'],2)
    df['a_loses_mean'] = round(df['a_loses'] / df['a_matches_played'],2)
    df['a_goals_for_mean'] = round(df['a_goals_for'] / df['a_matches_played'],2)
    df['a_goals_against_mean'] = round(df['a_goals_against'] / df['a_matches_played'],2)
    df['a_points_mean'] = round(df['a_points'] / df['a_matches_played'],2)
    
    df['a_winners_home_mean'] = round(df['a_winners_home'] / df['a_matches_played_home'],2)
    df['a_draws_home_mean'] =  round(df['a_draws_home'] / df['a_matches_played_home'],2)
    df['a_loses_home_mean'] =  round(df['a_loses_home'] / df['a_matches_played_home'],2)
    df['a_goals_for_home_mean'] =  round(df['a_goals_for_home'] / df['a_matches_played_home'],2)
    df['a_goals_against_home_mean'] = round(df['a_goals_against_home'] / df['a_matches_played_home'],2)
    df['a_points_home_mean'] = round(df['a_points_home'] / df['a_matches_played_home'],2)
    
    df['a_winners_away_mean'] = round(df['a_winners_away'] / df['a_matches_played_away'] ,2)       
    df['a_draws_away_mean'] = round(df['a_draws_away'] / df['a_matches_played_away'],2)        
    df['a_loses_away_mean'] = round(df['a_loses_away'] / df['a_matches_played_away'] ,2)   
    df['a_goals_for_away_mean'] = round(df['a_goals_for_away'] / df['a_matches_played_away'],2)    
    df['a_goals_against_away_mean'] = round(df['a_goals_against_away'] / df['a_matches_played_away'] ,2)   
    df['a_points_away_mean'] = round(df['a_points_away'] / df['a_matches_played_away'],2)
    
    df['h_winners_mean'].fillna(0, inplace=True)
    df['h_draws_mean'].fillna(0, inplace=True)
    df['h_loses_mean'].fillna(0, inplace=True)
    df['h_goals_for_mean'].fillna(0, inplace=True)
    df['h_goals_against_mean'].fillna(0, inplace=True)
    df['h_points_mean'].fillna(0, inplace=True)
    
    df['h_winners_home_mean'].fillna(0, inplace=True)
    df['h_draws_home_mean'].fillna(0, inplace=True)
    df['h_loses_home_mean'].fillna(0, inplace=True)
    df['h_goals_for_home_mean'].fillna(0, inplace=True)
    df['h_goals_against_home_mean'].fillna(0, inplace=True)
    df['h_points_home_mean'].fillna(0, inplace=True)
    
    df['h_winners_away_mean'].fillna(0, inplace=True)     
    df['h_draws_away_mean'].fillna(0, inplace=True)       
    df['h_loses_away_mean'].fillna(0, inplace=True)
    df['h_goals_for_away_mean'].fillna(0, inplace=True)    
    df['h_goals_against_away_mean'].fillna(0, inplace=True)    
    df['h_points_away_mean'].fillna(0, inplace=True)           
    
    df['a_winners_mean'].fillna(0, inplace=True)
    df['a_draws_mean'].fillna(0, inplace=True)
    df['a_loses_mean'].fillna(0, inplace=True)
    df['a_goals_for_mean'].fillna(0, inplace=True)
    df['a_goals_against_mean'].fillna(0, inplace=True)
    df['a_points_mean'].fillna(0, inplace=True)
    
    df['a_winners_home_mean'].fillna(0, inplace=True)
    df['a_draws_home_mean'] =  round(df['a_draws_home'] / df['a_matches_played_home'],2)
    df['a_loses_home_mean'] =  round(df['a_loses_home'] / df['a_matches_played_home'],2)
    df['a_goals_for_home_mean'] =  round(df['a_goals_for_home'] / df['a_matches_played_home'],2)
    df['a_goals_against_home_mean'] = round(df['a_goals_against_home'] / df['a_matches_played_home'],2)
    df['a_points_home_mean'] = round(df['a_points_home'] / df['a_matches_played_home'],2)
    
    df['a_winners_away_mean'] = round(df['a_winners_away'] / df['a_matches_played_away'] ,2)       
    df['a_draws_away_mean'] = round(df['a_draws_away'] / df['a_matches_played_away'],2)        
    df['a_loses_away_mean'] = round(df['a_loses_away'] / df['a_matches_played_away'] ,2)   
    df['a_goals_for_away_mean'] = round(df['a_goals_for_away'] / df['a_matches_played_away'],2)    
    df['a_goals_against_away_mean'] = round(df['a_goals_against_away'] / df['a_matches_played_away'] ,2)   
    df['a_points_away_mean'] = round(df['a_points_away'] / df['a_matches_played_away'],2)
         
    df.to_csv(path.NOTEBOOKS_DATA + 'matches-tables.csv',index=False);
                

#toForest()


def getFeatures1():
   
    TChampionship = aliased(Championship, name='c')
    TMatch = aliased(Match, name='m')
    Home = aliased(Table, name="h")
    Away = aliased(Table, name="a")
    
    
    results = session.query(TChampionship, TMatch, Home, Away).filter(
        TChampionship.id == TMatch.championshipId,
        TMatch.homeTeamId == Home.teamId, TMatch.awayTeamId == Away.teamId, 
        TMatch.id == Home.nextMatchId, TMatch.id == Away.nextMatchId).order_by(TMatch.id)

    print(results.count())
        # with_labels() beacause exists ambiguous columns name.
    df = pd.read_sql(results.with_labels().statement, session.bind)
    
    odds_favorite = []
    odds_medium = []
    odds_underdog = []
    favorites = []
    mediums = []
    underdogs = []
    
    
    for r in results.all():
        
        match = r[1]
        
        try:
            odds_favorite.append(match.favorite_odd())
        except:
            odds_favorite.append(None)
            
        try:
            odds_medium.append(match.medium_odd())
        except:
            odds_medium.append(None)
            
        try:
            odds_underdog.append(match.underdog_odd())
        except:
            odds_underdog.append(None)
       
        try:
            favorites.append(match.favorite())
        except:
            favorites.append(None)
            
        try:
            mediums.append(match.medium())
        except:
            mediums.append(None)
            
        try:
            underdogs.append(match.underdog())
        except:
            underdogs.append(None)
    
    df['m_odd_favorite'] = odds_favorite
    df['m_odd_medium'] = odds_medium
    df['m_odd_underdog'] = odds_underdog
    df['m_favorite'] = favorites
    df['m_medium'] = mediums
    df['m_underdog'] = underdogs
    
    df['h_wins_mean'] = round(df['h_wins'] / df['h_matches_played'],2)
    df['h_draws_mean'] = round(df['h_draws'] / df['h_matches_played'],2)
    df['h_loses_mean'] = round(df['h_loses'] / df['h_matches_played'],2)
    df['h_goals_for_mean'] = round(df['h_goals_for'] / df['h_matches_played'],2)
    df['h_goals_against_mean'] = round(df['h_goals_against'] / df['h_matches_played'],2)
    df['h_points_mean'] = round(df['h_points'] / df['h_matches_played'],2)
    
    df['h_wins_home_mean'] = round(df['h_wins_home'] / df['h_matches_played_home'],2)
    df['h_draws_home_mean'] =  round(df['h_draws_home'] / df['h_matches_played_home'],2)
    df['h_loses_home_mean'] =  round(df['h_loses_home'] / df['h_matches_played_home'],2)
    df['h_goals_for_home_mean'] =  round(df['h_goals_for_home'] / df['h_matches_played_home'],2)
    df['h_goals_against_home_mean'] = round(df['h_goals_against_home'] / df['h_matches_played_home'],2)
    df['h_points_home_mean'] = round(df['h_points_home'] / df['h_matches_played_home'],2)
    
    df['h_wins_away_mean'] = round(df['h_wins_away'] / df['h_matches_played_away'],2)        
    df['h_draws_away_mean'] = round(df['h_draws_away'] / df['h_matches_played_away'],2)        
    df['h_loses_away_mean'] = round(df['h_loses_away'] / df['h_matches_played_away'],2)    
    df['h_goals_for_away_mean'] = round(df['h_goals_for_away'] / df['h_matches_played_away'],2)    
    df['h_goals_against_away_mean'] = round(df['h_goals_against_away'] / df['h_matches_played_away'],2)    
    df['h_points_away_mean'] = round(df['h_points_away'] / df['h_matches_played_away'],2)            
    
    df['a_wins_mean'] = round(df['a_wins'] / df['a_matches_played'],2)
    df['a_draws_mean'] = round(df['a_draws'] / df['a_matches_played'],2)
    df['a_loses_mean'] = round(df['a_loses'] / df['a_matches_played'],2)
    df['a_goals_for_mean'] = round(df['a_goals_for'] / df['a_matches_played'],2)
    df['a_goals_against_mean'] = round(df['a_goals_against'] / df['a_matches_played'],2)
    df['a_points_mean'] = round(df['a_points'] / df['a_matches_played'],2)
    
    df['a_wins_home_mean'] = round(df['a_wins_home'] / df['a_matches_played_home'],2)
    df['a_draws_home_mean'] =  round(df['a_draws_home'] / df['a_matches_played_home'],2)
    df['a_loses_home_mean'] =  round(df['a_loses_home'] / df['a_matches_played_home'],2)
    df['a_goals_for_home_mean'] =  round(df['a_goals_for_home'] / df['a_matches_played_home'],2)
    df['a_goals_against_home_mean'] = round(df['a_goals_against_home'] / df['a_matches_played_home'],2)
    df['a_points_home_mean'] = round(df['a_points_home'] / df['a_matches_played_home'],2)
    
    df['a_wins_away_mean'] = round(df['a_wins_away'] / df['a_matches_played_away'] ,2)       
    df['a_draws_away_mean'] = round(df['a_draws_away'] / df['a_matches_played_away'],2)        
    df['a_loses_away_mean'] = round(df['a_loses_away'] / df['a_matches_played_away'] ,2)   
    df['a_goals_for_away_mean'] = round(df['a_goals_for_away'] / df['a_matches_played_away'],2)    
    df['a_goals_against_away_mean'] = round(df['a_goals_against_away'] / df['a_matches_played_away'] ,2)   
    df['a_points_away_mean'] = round(df['a_points_away'] / df['a_matches_played_away'],2)
    
    df['h_wins_mean'].fillna(0, inplace=True)
    df['h_draws_mean'].fillna(0, inplace=True)
    df['h_loses_mean'].fillna(0, inplace=True)
    df['h_goals_for_mean'].fillna(0, inplace=True)
    df['h_goals_against_mean'].fillna(0, inplace=True)
    df['h_points_mean'].fillna(0, inplace=True)
    
    df['h_wins_home_mean'].fillna(0, inplace=True)
    df['h_draws_home_mean'].fillna(0, inplace=True)
    df['h_loses_home_mean'].fillna(0, inplace=True)
    df['h_goals_for_home_mean'].fillna(0, inplace=True)
    df['h_goals_against_home_mean'].fillna(0, inplace=True)
    df['h_points_home_mean'].fillna(0, inplace=True)
    
    df['h_wins_away_mean'].fillna(0, inplace=True)     
    df['h_draws_away_mean'].fillna(0, inplace=True)       
    df['h_loses_away_mean'].fillna(0, inplace=True)
    df['h_goals_for_away_mean'].fillna(0, inplace=True)    
    df['h_goals_against_away_mean'].fillna(0, inplace=True)    
    df['h_points_away_mean'].fillna(0, inplace=True)           
    
    df['a_wins_mean'].fillna(0, inplace=True)
    df['a_draws_mean'].fillna(0, inplace=True)
    df['a_loses_mean'].fillna(0, inplace=True)
    df['a_goals_for_mean'].fillna(0, inplace=True)
    df['a_goals_against_mean'].fillna(0, inplace=True)
    df['a_points_mean'].fillna(0, inplace=True)
    
    df['a_wins_home_mean'].fillna(0, inplace=True)
    df['a_draws_home_mean'].fillna(0, inplace=True)
    df['a_loses_home_mean'].fillna(0, inplace=True)
    df['a_goals_for_home_mean'].fillna(0, inplace=True)
    df['a_goals_against_home_mean'].fillna(0, inplace=True)
    df['a_points_home_mean'].fillna(0, inplace=True)
    
    df['a_wins_away_mean'].fillna(0, inplace=True)    
    df['a_draws_away_mean'].fillna(0, inplace=True)      
    df['a_loses_away_mean'].fillna(0, inplace=True)  
    df['a_goals_for_away_mean'].fillna(0, inplace=True)   
    df['a_goals_against_away_mean'].fillna(0, inplace=True)   
    df['a_points_away_mean'].fillna(0, inplace=True)
    
    df.to_csv(path.NOTEBOOKS_DATA + 'features1.csv',index=False);
    
    

   
#remove brazil - serie b and matches without odds    
def getFeatures2():
    
    df = pd.read_csv(path.NOTEBOOKS_DATA + 'features1.csv')
    df = df[(df.m_championship_id < 11) | (df.m_championship_id > 20)].sort_values(['m_championship_id','m_match_date'])
    df = df[df.m_odd_home.notnull()]
    df = df[df.m_odd_draw.notnull()]
    df = df[df.m_odd_away.notnull()] 
    
    df['m_favorite_num'] = df['m_favorite'].apply(categoricalToInt)
    df['m_medium_num'] = df['m_medium'].apply(categoricalToInt)
    df['m_underdog_num'] = df['m_underdog'].apply(categoricalToInt)
    
    df.to_csv(path.NOTEBOOKS_DATA + 'features2.csv',index=False);
   
def categoricalToInt(row):

    if (row == 'H'):
        return 0
    elif (row == 'D'):
        return 1
    else:
        return 2


def forestPredict(columName, features, trees):
    
    pd.options.mode.chained_assignment = None
    
    df = pd.read_csv(path.NOTEBOOKS_DATA + 'features2.csv')
    df['pred'] = ""
    #df = df.set_index([df.m_championship_id,df.m_match_group_num])
    df = df.set_index([df.m_match_id])
    
    for champId in range(1,91):
        
        champ = df[(df.m_championship_id == champId)]       
        print(champId)
        
        if (champId < 11 or champId > 20):
            
            if (len(champ) == 380):
                rd = 38
            elif (len(champ) == 306):
                rd = 34
            else:
                rd = 30
                 
            for mid in range(2,rd+1):
                
                train = champ[champ.m_match_group_num < mid]
                test = champ[champ.m_match_group_num == mid]
                  
                target = 'm_column_result'
                  
                X = train[features]
                y = train[target]                  
                Z = test[features]
                  
                clf = RandomForestClassifier(n_estimators=trees,max_features=None )
                clf.fit(X,y)
                          
                pred = clf.predict(Z)
                  
                for i,p in zip(Z.index,pred) :

                    df.set_value(i,'pred',p)
             
    nameFile = 'pred_' + columName + ".csv"
    
    df.to_csv(path.NOTEBOOKS_DATA + nameFile,index=False);


def forestPredict7030(columName, features, trees):
    
    pd.options.mode.chained_assignment = None
    
    df = pd.read_csv(path.NOTEBOOKS_DATA + 'features2.csv')
    df['pred'] = ""
    #df = df.set_index([df.m_championship_id,df.m_match_group_num])
    df = df.set_index([df.m_match_id])
    
    for champId in range(11,91,10):
        
        champ = df[(df.m_championship_id < champId) & (df.m_championship_id >= champId-10)]       
        
        print(champId)
        
        if (champId != 21):
            
                train = champ[df.m_championship_id <= champId-4]
                test = champ[df.m_championship_id > champId-4]
                  
                target = 'm_column_result'
                  
                X = train[features]
                y = train[target]                  
                Z = test[features]
                  
                clf = RandomForestClassifier(n_estimators=trees,max_features=None )
                clf.fit(X,y)
                          
                pred = clf.predict(Z)
                  
                for i,p in zip(Z.index,pred) :

                    df.set_value(i,'pred',p)
             
    nameFile = 'pred_' + columName + ".csv"
    
    df.to_csv(path.NOTEBOOKS_DATA + nameFile,index=False);
    
def main():
    
    print("a")
  
    features = ['m_odd_home','m_odd_away','m_odd_underdog',
            'm_odd_favorite','m_odd_draw','m_odd_medium',
            'a_goals_for','h_goals_for',
            'h_goals_against','a_goals_against',
            'a_points','h_points','a_goals_for_home',
            'h_goals_against_away', 'h_goals_for_home',
            'h_goals_for_away','a_goals_against_home',
            'a_goals_against_away','a_goals_for_away',
            'h_goals_against_home','h_team_id','a_team_id',
            'h_points_away','h_points_away','h_draws',
            'h_wins','a_points_home','a_draws','a_wins',
            'a_points_away','a_loses','h_loses','h_points_home']
    
    
    forestPredict('rf14',features,1000)
    
    
#     features = ['m_odd_home','m_odd_away','m_odd_underdog',
#                         'm_odd_favorite','m_odd_draw','m_odd_medium']
#                  
#     forestPredict('rf1',features,1000)
#      
#     features = ['m_odd_home','m_odd_away','m_odd_underdog',
#                         'm_odd_favorite','m_odd_draw','m_odd_medium',
#                         'a_goals_for_mean','h_goals_for_mean']
#                  
#     forestPredict('rf2',features,1000)
#     
#     features = ['m_odd_home','m_odd_away','m_odd_underdog',
#             'm_odd_favorite','m_odd_draw','m_odd_medium',
#             'a_goals_for_mean','h_goals_for_mean',
#             'h_goals_against_mean','a_goals_against_mean',
#             'a_points_mean','h_points_mean','a_goals_for_home_mean',
#             'h_goals_against_away_mean', 'h_goals_for_home_mean',
#             'h_goals_for_away_mean','a_goals_against_home_mean',
#             'a_goals_against_away_mean','a_goals_for_away_mean',
#             'h_goals_against_home_mean','h_team_id','a_team_id',
#             'h_points_away_mean','h_points_away_mean','h_draws_mean',
#             'h_wins_mean','a_points_home_mean','a_draws_mean','a_wins_mean',
#             'a_points_away_mean','a_loses_mean','h_loses_mean','h_points_home_mean']
#      
#     forestPredict('rf3',features,1000)
# 
#     features = [
#             'a_goals_for_mean','h_goals_for_mean',
#             'h_goals_against_mean','a_goals_against_mean',
#             'a_points_mean','h_points_mean','a_goals_for_home_mean',
#             'h_goals_against_away_mean', 'h_goals_for_home_mean',
#             'h_goals_for_away_mean','a_goals_against_home_mean',
#             'a_goals_against_away_mean','a_goals_for_away_mean',
#             'h_goals_against_home_mean','h_team_id','a_team_id',
#             'h_points_away_mean','h_points_away_mean','h_draws_mean',
#             'h_wins_mean','a_points_home_mean','a_draws_mean','a_wins_mean',
#             'a_points_away_mean','a_loses_mean','h_loses_mean','h_points_home_mean']
#      
#     forestPredict('rf4',features,1000)
    
#     features = ['m_odd_home','m_odd_away','m_odd_underdog',
#                         'm_odd_favorite','m_odd_draw','m_odd_medium']
#                  
#     forestPredict('rf5',features,100)
#      
#     features = ['m_odd_home','m_odd_away','m_odd_underdog',
#                         'm_odd_favorite','m_odd_draw','m_odd_medium',
#                         'a_goals_for_mean','h_goals_for_mean']
#                  
#     forestPredict('rf6',features,100)
#     
#     features = ['m_odd_home','m_odd_away','m_odd_underdog',
#             'm_odd_favorite','m_odd_draw','m_odd_medium',
#             'a_goals_for_mean','h_goals_for_mean',
#             'h_goals_against_mean','a_goals_against_mean',
#             'a_points_mean','h_points_mean','a_goals_for_home_mean',
#             'h_goals_against_away_mean', 'h_goals_for_home_mean',
#             'h_goals_for_away_mean','a_goals_against_home_mean',
#             'a_goals_against_away_mean','a_goals_for_away_mean',
#             'h_goals_against_home_mean','h_team_id','a_team_id',
#             'h_points_away_mean','h_points_away_mean','h_draws_mean',
#             'h_wins_mean','a_points_home_mean','a_draws_mean','a_wins_mean',
#             'a_points_away_mean','a_loses_mean','h_loses_mean','h_points_home_mean']
#      
#     forestPredict('rf7',features,100)
# 
#     features = [
#             'a_goals_for_meanchamp = df[(df.m_championship_id < t1) & (df.m_championship_id >= t1-10)].sort_values(['m_match_date'])','h_goals_for_mean',
#             'h_goals_against_mean','a_goals_against_mean',
#             'a_points_mean','h_points_mean','a_goals_for_home_mean',
#             'h_goals_against_away_mean', 'h_goals_for_home_mean',
#             'h_goals_for_away_mean','a_goals_against_home_mean',
#             'a_goals_against_away_mean','a_goals_for_away_mean',
#             'h_goals_against_home_mean','h_team_id','a_team_id',
#             'h_points_away_mean','h_points_away_mean','h_draws_mean',
#             'h_wins_mean','a_points_home_mean','a_draws_mean','a_wins_mean',
#             'a_points_away_mean','a_loses_mean','h_loses_mean','h_points_home_mean']
#      
#     forestPredict('rf8',features,100)
    
#     df = pd.read_csv(path.NOTEBOOKS_DATA + 'features2.csv')
#     features = list(df.columns)
#     
#     
#     features.remove('m_match_id')
#     features.remove('m_goals_home')
#     features.remove('m_goals_away')
#     features.remove('m_column_result')
#     features.remove('m_match_date')
#     features.remove('h_next_match_id')
#     features.remove('a_next_match_id')
#     features.remove('m_favorite')
#     features.remove('m_medium')
#     features.remove('m_underdog')
#     features.remove('a_last_match_local')
#     features.remove('h_last_match_local')
#     
#     print(features)
#     
#     forestPredict('rf9',features,100)
#     forestPredict('rf10',features,1000)
#     forestPredict('rf11',features,2000)
       
#     features = ['m_odd_home','m_odd_away','m_odd_underdog',
#                         'm_odd_favorite','m_odd_draw','m_odd_medium',
#                         'a_goals_for_mean','h_goals_for_mean']
#                   
#     forestPredict7030('rf12',features,1000)
#     
#     features = ['m_odd_home','m_odd_away','m_odd_underdog',
#             'm_odd_favorite','m_odd_draw','m_odd_medium',
#             'a_goals_for_mean','h_goals_for_mean',
#             'h_goals_against_mean','a_goals_against_mean',
#             'a_points_mean','h_points_mean','a_goals_for_home_mean',
#             'h_goals_against_away_mean', 'h_goals_for_home_mean',
#             'h_goals_for_away_mean','a_goals_against_home_mean',
#             'a_goals_against_away_mean','a_goals_for_away_mean',
#             'h_goals_against_home_mean','h_team_id','a_team_id',
#             'h_points_away_mean','h_points_away_mean','h_draws_mean',
#             'h_wins_mean','a_points_home_mean','a_draws_mean','a_wins_mean',
#             'a_points_away_mean','a_loses_mean','h_loses_mean','h_points_home_mean']
#     
#     forestPredict7030('rf13',features,1000)

def forestPredict4():
    
    df = pd.read_csv(path.NOTEBOOKS_DATA + 'features3.csv')
    
    df.index = df.m_match_id
    df['rf1000_fs4'] = ""
    pd.options.mode.chained_assignment = None

    
    for t1 in range(11,91,10):
        
        print(t1)
        
        champ = df[(df.m_championship_id < t1) & (df.m_championship_id >= t1-10)].sort_values(['m_match_date'])        
        
        for t2 in range(10,len(champ),10):
              
            train = champ[0:t2]
            test = champ[t2:t2+10]
              
            features = ['m_odd_home','m_odd_away','m_odd_underdog',
                        'm_odd_favorite','m_odd_draw','m_odd_medium',
                        'a_goals_for_mean','h_goals_for_mean']
              
            target = 'm_column_result'
              
            X = train[features]
            y = train[target]             
            Z = test[features]
              
            clf = RandomForestClassifier(n_estimators=1000)
            clf.fit(X,y)
                      
            pred = clf.predict(Z)
              
            for t3,p in zip(Z.index,pred) :
                df.set_value(t3,'rf1000_fs4',p)
        
 
    df.to_csv(path.NOTEBOOKS_DATA + 'features3.csv',index=False);        

def accuracy():
    
    
    df = pd.read_csv(path.NOTEBOOKS_DATA + 'features3.csv')
    df = df[df.rf1000.isnull() == False]
    tamanho = len(df)
    
    print(len(df))
    a = len(df[df.m_column_result == df.m_favorite])
    b = len(df[df.m_column_result == df.rf1000])
    print(a)
    print(b)
    
    print(a/tamanho)
    print(b/tamanho)
    
    c = len(df[(df.m_column_result == df.m_favorite) & (df.m_favorite == 'H')])
    ctam = len(df[(df.m_favorite == 'H')])
    
    d = len(df[(df.m_column_result == df.rf1000) & (df.rf1000 == 'H')])
    dtam = len(df[(df.rf1000 == 'H')])
    
    print(c/ctam)
    print(d/dtam)
    
    f = len(df[(df.m_column_result == df.rf1000) & (df.m_favorite == 'H')])
    print(f)
    print(f/ctam)
    
def matchNumber():
    
    df = pd.read_csv(path.NOTEBOOKS_DATA + 'features3.csv')
    
    df.index = df.m_match_id   
    pd.options.mode.chained_assignment = None
    
    for t1 in range(31,41):
        
        champ = df[(df.m_championship_id == t1)].sort_values(['m_match_date'])
        print(t1)
          
        lista = champ[40:len(champ)]
                            
        tam1 = len(lista[lista.m_favorite == 'H'])
        tam2 = len(lista[lista.m_favorite == 'D'])
        tam3 = len(lista[lista.m_favorite == 'A'])
        
        
        a1 = len(lista[(lista.m_column_result == lista.m_favorite) & (lista.m_favorite == 'H')])
        a2 = len(lista[(lista.m_column_result == lista.m_favorite) & (lista.m_favorite == 'D')])
        a3 = len(lista[(lista.m_column_result == lista.m_favorite) & (lista.m_favorite == 'A')])
            
        print(tam1+tam2+tam3)
        print(a1+a2+a3)
        print(tam1)
        print(tam2)
        print(tam3)
        print(a1)
        print(a2)
        print(a3)
        
        if((a1 > 0) & (tam1 > 0)):
            print(round(a1/tam1,2))
        else:
            print(0)
            
        if((a2 > 0) & (tam2 > 0)):
            print(round(a2/tam2,2))
        else:
            print(0)
            
        if((a3 > 0) & (tam3 > 0)):
            print(round(a3/tam3,2))
        else:
            print(0)
            
    print('-----')
    for t1 in range(31,41):
        
        champ = df[(df.m_championship_id == t1)].sort_values(['m_match_date'])
        print(t1)
          
        lista = champ[40:len(champ)]
                            
        tam1 = len(lista[lista.rf1000 == 'H'])
        tam2 = len(lista[lista.rf1000 == 'D'])
        tam3 = len(lista[lista.rf1000 == 'A'])
        
        
        a1 = len(lista[(lista.m_column_result == lista.rf1000) & (lista.rf1000 == 'H')])
        a2 = len(lista[(lista.m_column_result == lista.rf1000) & (lista.rf1000 == 'D')])
        a3 = len(lista[(lista.m_column_result == lista.rf1000) & (lista.rf1000 == 'A')])
            
        print(tam1+tam2+tam3)
        print(a1+a2+a3)
        print(tam1)
        print(tam2)
        print(tam3)
        print(a1)
        print(a2)
        print(a3)
        
        if((a1 > 0) & (tam1 > 0)):
            print(round(a1/tam1,2))
        else:
            print(0)
            
        if((a2 > 0) & (tam2 > 0)):
            print(round(a2/tam2,2))
        else:
            print(0)
            
        if((a3 > 0) & (tam3 > 0)):
            print(round(a3/tam3,2))
        else:
            print(0)
             

def importance():
    
    df = pd.read_csv(path.NOTEBOOKS_DATA + 'features3.csv')

    features = list(df.columns.values)
    
    target = 'm_column_result'
    features.remove('m_match_id')
    features.remove('m_column_result')
    features.remove('m_match_date')
    features.remove('m_goals_home')
    features.remove('m_goals_away')
    features.remove('a_next_match_id')
    features.remove('h_next_match_id')
    features.remove('m_favorite')
    features.remove('m_medium')
    features.remove('m_underdog')
    features.remove('h_last_match_local')
    features.remove('a_last_match_local')
    features.remove('rf1000')
    features.remove('rf1000_fs1')
    
    
    X = df[features]
    y = df[target]
    # fit an Extra Trees model to the data
    clf = RandomForestClassifier(n_estimators=1000)
    clf.fit(X, y)
    # display the relative importance of each attribute
    for x,y in zip(features,clf.feature_importances_):
        
        print (x,y)

#importance()

def matchNumber2():
    
    df = pd.read_csv(path.NOTEBOOKS_DATA + 'features3.csv')
    
    df.index = df.m_match_id   
    pd.options.mode.chained_assignment = None
    
    for t1 in range(31,41):
        
        champ = df[(df.m_championship_id == t1)].sort_values(['m_match_date'])
        print(t1)
          
        lista = champ[40:len(champ)]
                            
        tam1 = len(lista[lista.rf1000_fs1 == 'H'])
        tam2 = len(lista[lista.rf1000_fs1 == 'D'])
        tam3 = len(lista[lista.rf1000_fs1 == 'A'])
        
        
        a1 = len(lista[(lista.m_column_result == lista.rf1000_fs1) & (lista.rf1000 == 'H')])
        a2 = len(lista[(lista.m_column_result == lista.rf1000_fs1) & (lista.rf1000 == 'D')])
        a3 = len(lista[(lista.m_column_result == lista.rf1000_fs1) & (lista.rf1000 == 'A')])
            
        print(tam1+tam2+tam3)
        print(a1+a2+a3)
        print(tam1)
        print(tam2)
        print(tam3)
        print(a1)
        print(a2)
        print(a3)
        
        if((a1 > 0) & (tam1 > 0)):
            print(round(a1/tam1,2))
        else:
            print(0)
            
        if((a2 > 0) & (tam2 > 0)):
            print(round(a2/tam2,2))
        else:
            print(0)
            
        if((a3 > 0) & (tam3 > 0)):
            print(round(a3/tam3,2))
        else:
            print(0)


def rfOddFavorite(row):

    if (row == 'H'):
        return 0
    elif (row == 'D'):
        return 1
    else:
        return 2
    
def getFeatures3():
    
    df = pd.read_csv(path.NOTEBOOKS_DATA + 'features3.csv')
    
    df.index = df.m_match_id
    pd.options.mode.chained_assignment = None
    
    match_num = []
    
    for t1 in range(1,91):
        
        champ = df[(df.m_championship_id == t1)].sort_values(['m_match_date'])
          
        for t2 in range(0,len(champ),1):
              
            match_num.append(t2+1)
             
 
    print(match_num)
    df['m_match_num'] = match_num
    df.to_csv(path.NOTEBOOKS_DATA + 'features4.csv',index=False);
   
#getFeatures1()
#getFeatures2()
main()



#getFeatures3()
# def teste():
#     
#     df = pd.read_csv(path.NOTEBOOKS_DATA + 'features1.csv')
#     pd.set_option('display.max_rows', 500)
#     g = df['m_match_id'].groupby(df.m_championship_id).count()
#     
#     print(g)
#     
# def teste2():
#     
#     df = pd.read_csv(path.NOTEBOOKS_DATA + 'features2.csv')
#     pd.set_option('display.max_rows', 500)
#     g = df['m_match_id'].groupby(df.m_championship_id).count()
#     
#     print(g)
#     