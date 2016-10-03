'''
Created on 3 de out de 2016

@author: igormago
'''
from datetime import datetime
import os, requests

from bs4 import BeautifulSoup

from core import utils
from explorer import models
from explorer.models import Championship, Match, Team

session = models.getSession()

def crawlerChampionshipFiles(year, tourneament):

    tourneamentName = tourneament + "-" + str(year)

    url = utils.URL_BETEXPLORER + tourneamentName + "/results/"
    fileName = utils.PATH_BETEXPLORER_CHAMPS + tourneamentName + ".html"

    if (not os.path.exists(fileName)):
        print("NÃO EXISTE o ARQUIVO: ", fileName)
        r = requests.get(url, stream=True)

        file = open(fileName, 'wb')
        file.write(r.content)
        file.close()
        
    else:
        print("JÁ EXISTE O ARQUIVO: ", fileName)
        
    try:
        session.add(Championship(name=tourneament, year=year))
        session.commit()
    except:
        print("JA EXISTE NO BANCO:" + fileName)
        pass
                
def scrapChampionshipFiles():

    championships = Championship.list()

    for c in championships:

        fileName = utils.PATH_BETEXPLORER_CHAMPS + c.getFileName()
        print("SCRAPING: " + fileName)
        file = open(fileName, 'r')

        content = file.read()

        soup = BeautifulSoup(content, 'html.parser')

        text = soup.find(id="leagueresults_tbody")
        trs = text.find_all("tr")

        line = 0
        match = Match()

        for tr in trs:

            if (tr['class'][0] == 'rtitle'):
                roundNum = tr.getText().split(".")[0]
            else:

                tds = tr.find_all('td')

                for td in tds:
                    line = line + 1
                    if (line == 1):
                        match = Match()

                        a = td.find('a')
                        match.id = a['href'].split("=")[1]

                        homeTeamName = td.getText().split(" - ")[0].strip()
                        awayTeamName = td.getText().split(" - ")[1].strip()

                        try:
                            homeTeam = session.query(Team).filter(Team.name==homeTeamName)
                            homeTeam = homeTeam.one()
                        except:
                            homeTeam = Team(name=homeTeamName)
                            session.add(homeTeam)
                            session.commit()

                        try:
                            awayTeam = session.query(Team).filter(Team.name==awayTeamName).one()
                        except:
                            awayTeam = Team(name=awayTeamName)
                            session.add(awayTeam)
                            session.commit()

                        match.homeTeamId = homeTeam.id
                        match.awayTeamId = awayTeam.id
                        match.roundNum = roundNum
                        match.championshipId = c.id

                    elif (line == 2):
                        match.goalsHome = td.getText().split(':')[0]
                        match.goalsAway = td.getText().split(':')[1].split()[0]

                    elif (line == 3):
                        try:
                            match.oddsHome = td['data-odd']
                        except:
                            match.oddsHome = None

                    elif (line == 4):
                        try:
                            match.oddsDraw = td['data-odd']
                        except:
                            match.oddsDraw = None

                    elif (line == 5):
                        try:
                            match.oddsAway = td['data-odd']
                        except:
                            match.oddsAway = None

                    elif (line == 6):
                        dateStr = td.getText()
                        match.matchDate = datetime.strptime(dateStr,"%d.%m.%Y")
                        line = 0

                        try:
                            session.add(match)
                            session.commit()
                        except:
                            session.rollback()
                            match = session.query(Match).filter(Match.id==match.id)
#          
# def crawlerMatchFiles():
# 
#     matches = session.query(Match)
# 
#     for match in matches:
# 
#         url = "http://www.betexplorer.com//gres/ajax-matchodds.php"
# 
#         types = {'1x2', 'ou', 'ah', 'ha', 'dc', 'bts'}
#         params = {}
#         params['t'] = 'n'
#         params['e'] = match.id
# 
#         for oddType in types:
# 
#             params['b'] = oddType
#             fileName = utils.PATH_BETEXPLORER_MATCHES + match.getFileName(oddType)
# 
#             if (os.path.exists(fileName)):
#                 print("JA EXISTE: ", )
#             else:
#                 r = requests.get(url,params=params)
# 
#                 file = open(fileName,'wb')
#                 file.write(r.content)
#                 file.close()   
