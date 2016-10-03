'''
Created on 3 de out de 2016

@author: igormago
'''
from core.utils import BRAZILIAN_SERIE_A, BRAZILIAN_SERIE_B
from explorer import services as s

def crawlerChampionshipFile():
    
    for year in range (2006, 2016):
        s.crawlerChampionshipFiles(year, BRAZILIAN_SERIE_A)
        s.crawlerChampionshipFiles(year, BRAZILIAN_SERIE_B)


#crawlerChampionshipFile()
s.scrapChampionshipFiles()