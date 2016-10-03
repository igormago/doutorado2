'''
Created on 3 de out de 2016

@author: igormago
'''

PATH_PROJECT = "/home/igormago/git/doutorado/"
PATH_FILES = PATH_PROJECT + "files/"
PATH_BETEXPLORER_FILES = PATH_FILES + "explorer/"
PATH_BETEXPLORER_CHAMPS = PATH_BETEXPLORER_FILES + "championships/"
PATH_BETEXPLORER_MATCHES = PATH_BETEXPLORER_FILES + "matches/"

URL_BETEXPLORER="http://www.betexplorer.com/soccer/brazil/"
NOTEBOOKS_CSV = PATH_PROJECT + "/notebooks/csv/"

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

BRAZILIAN_SERIE_A = 'serie-a'
BRAZILIAN_SERIE_B = 'serie-b'