'''
Created on 3 de out de 2016

@author: igormago
'''
from explorer import services as s
from core.utils import Championships as c
from explorer.models import Match

def crawlerChampionshipFile(championship,typeChamp):
    for year in range (2006, 2016):
        s.crawlerChampionshipFiles(year, championship, typeChamp)
    
def crawlerMatchFiles():
    matches = Match.list()
    for m in matches:
        s.crawlerMatchFiles(m.id)

def scrapChampionshipFile(championship):
    for year in range(2006,2016):
        s.scrapChampionshipFile(championship, year)
        
        
crawlerChampionshipFile(c.BRAZIL_SERIE_A,1)
crawlerChampionshipFile(c.BRAZIL_SERIE_B,1)
crawlerChampionshipFile(c.SPAIN_LA_LIGA_1,2)
crawlerChampionshipFile(c.ENGLAND_PREMIER_LEAGUE,2)      
crawlerChampionshipFile(c.ITALY_SERIE_A,2)
crawlerChampionshipFile(c.FRANCE_LIGUE_1,2)
crawlerChampionshipFile(c.GERMANY_BUNDESLIGA,2)
crawlerChampionshipFile(c.PORTUGAL_PRIMEIRA_LIGA,2)
crawlerChampionshipFile(c.NETHERLANDS_EREDIVISIE,2)
crawlerChampionshipFile(c.TURKEY_SUPER_LIG,2)

scrapChampionshipFile(c.BRAZIL_SERIE_A)
scrapChampionshipFile(c.BRAZIL_SERIE_B)
scrapChampionshipFile(c.SPAIN_LA_LIGA_1)
scrapChampionshipFile(c.ENGLAND_PREMIER_LEAGUE)      
scrapChampionshipFile(c.ITALY_SERIE_A)
scrapChampionshipFile(c.FRANCE_LIGUE_1)
scrapChampionshipFile(c.GERMANY_BUNDESLIGA)
scrapChampionshipFile(c.PORTUGAL_PRIMEIRA_LIGA)
scrapChampionshipFile(c.NETHERLANDS_EREDIVISIE)
scrapChampionshipFile(c.TURKEY_SUPER_LIG)

import os
import shutil

path = '/home/igormago/git/doutorado/files/explorer/matches/Brasileirão - Série A/'
path2 = '/home/igormago/git/doutorado/files/explorer/matches/Brasileirão - Série B/'

'''
for nome in os.listdir(path):
    
    id = nome.split("-")[0]
    match = Match.get(id)
    if (match.championshipId > 10):
        shutil.move(path + nome, path2)

'''