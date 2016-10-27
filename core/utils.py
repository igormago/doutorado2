'''
Created on 3 de out de 2016

@author: igormago
'''


URL_BETEXPLORER="http://www.betexplorer.com/soccer/"
URL_BETEXPLORER_BRAZIL="http://www.betexplorer.com/soccer/brazil/"
URL_BETEXPLORER_SPAIN="http://www.betexplorer.com/soccer/spain/"
#NOTEBOOKS_CSV = PATH_PROJECT + "/notebooks/csv/"

TYPE_1x2 = '1x2'
TYPE_OU = 'ou'
TYPE_AH = 'ah'
TYPE_DNB = 'ha'
TYPE_DC = 'dc'
TYPE_BTS = 'bts'

ODD_AVG = 'avg'
ODD_MAX = 'max'
ODD_MIN = 'min'

ODDS_TYPES = {TYPE_1x2, TYPE_OU, TYPE_AH, TYPE_DNB, TYPE_DC, TYPE_BTS}

class Championships():
    
    BRAZIL_SERIE_A = ('Brazil - Série A','brazil/serie-a')
    BRAZIL_SERIE_B = ('Brazil - Série B','brazil/serie-b')
    SPAIN_LA_LIGA_1 = ('Spain - La Liga 1', 'spain/primera-division') 
    ENGLAND_PREMIER_LEAGUE = ('England - Premier League', 'england/premier-league')
    ITALY_SERIE_A = ('Italy - Serie A', 'italy/serie-a')
    FRANCE_LIGUE_1 = ('France - Ligue 1', 'france/ligue-1')
    GERMANY_BUNDESLIGA = ('Germany - Bundesliga', 'germany/bundesliga')
    PORTUGAL_PRIMEIRA_LIGA = ('Portugal - Primeira Liga', 'portugal/primeira-liga')
    NETHERLANDS_EREDIVISIE = ('Netherlands - Eredivise', 'netherlands/eredivisie')
    TURKEY_SUPER_LIG = ('Turkey - Super Lig', 'turkey/super-lig')
        
    @staticmethod
    def getFileName(championship, year):
        return championship + " - " + str(year) + ".html"
        
    
class Path():
    
    PROJECT = "/home/igormago/git/doutorado/"
    FILES = PROJECT + "files/"
    BETEXPLORER_FILES = FILES + "explorer/"
    BETEXPLORER_CHAMPS = BETEXPLORER_FILES + "championships/"
    BETEXPLORER_MATCHES = BETEXPLORER_FILES + "matches/"
    NOTEBOOKS_DATA = PROJECT + 'notebooks/data/'
    
class Features():

    CHAMPIONSHIP = 'CHAMP'
    TEAM = 'TEAM'
    LAST_MATCH_LOCAL = 'LML'
    WINNERS = 'W'
    DRAWS = 'D'
    LOSES = 'L'
    POINTS = 'P'
    GOALS_FOR = 'GF'
    GOALS_AGAINST = 'GA'
    GOALS_DIFFERENCE = 'GD'
    MATCHES_PLAYED = 'MP'
    WINNERS_HOME = 'WH'
    DRAWS_HOME = 'DH'
    LOSES_HOME = 'LH'
    POINTS_HOME = 'PH'
    GOALS_FOR_HOME = 'GFH'
    GOALS_AGAINST_HOME = 'GAH'
    GOALS_DIFFERENCE_HOME = 'GDH'
    MATCHES_PLAYED_HOME = 'MPH'
    WINNERS_AWAY = 'WA'
    DRAWS_AWAY = 'DA'
    LOSES_AWAY = 'LA'
    POINTS_AWAY = 'PA'
    GOALS_FOR_AWAY = 'GFA'
    GOALS_AGAINST_AWAY = 'GAA'
    GOALS_DIFFERENCE_AWAY = 'GDA'
    MATCHES_PLAYED_AWAY = 'MPA'
    