'''
Created on 3 de out de 2016

@author: igormago
'''
from datetime import datetime
import os, requests

from bs4 import BeautifulSoup

from core import utils
from core.utils import Championships as champ
from core.utils import Path as path
from explorer import models
from explorer.models import Championship, Match, Team, Table, Evaluation


session = models.getSession()

def crawlerChampionshipFiles(year, tourneament, typeChamp):
    
    if (typeChamp == 2):
        tourneamentYears = str(year) + "-" + str(year+1)
        url = utils.URL_BETEXPLORER + tourneament[1] + "-" + tourneamentYears + "/results/"
    else:
        url = utils.URL_BETEXPLORER + tourneament[1] + "-" + str(year) + "/results/"
    
    print(url)
    tourneamentName = tourneament[0] + " - " + str(year)

    fileName = path.BETEXPLORER_CHAMPS + tourneamentName + ".html"
    

    if (not os.path.exists(fileName)):
        print("NÃO EXISTE o ARQUIVO: ", fileName)
        r = requests.get(url, stream=True)

        file = open(fileName, 'wb')
        file.write(r.content)
        file.close()
        
    else:
        print("JÁ EXISTE O ARQUIVO: ", fileName)
        
    try:
        session.add(Championship(name=tourneament[0], year=year))
        session.commit()
    except:
        print("JA EXISTE NO BANCO:" + fileName)
        pass
                
def scrapChampionshipFiles():

    championships = Championship.list()

    for c in championships:

        fileName = path.BETEXPLORER_CHAMPS + c.getFileName()
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
                            match.oddHome = td['data-odd']
                        except:
                            match.oddHome = None

                    elif (line == 4):
                        try:
                            match.oddDraw = td['data-odd']
                        except:
                            match.oddDraw = None

                    elif (line == 5):
                        try:
                            match.oddAway = td['data-odd']
                        except:
                            match.oddAway = None

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
                            
def scrapChampionshipFile(championship, year):

    fileName = path.BETEXPLORER_CHAMPS + champ.getFileName(championship[0], year)
    champDB = Championship.get(championship[0], year)
    
    print("SCRAPING: " + fileName)
    file = open(fileName, 'r')
 
    content = file.read()

    soup = BeautifulSoup(content, 'html.parser')

    text = soup.find(id="leagueresults_tbody")
    trs = text.find_all("tr")

    line = 0
    match = Match()
    roundNum = 0
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
                    match.championshipId = champDB.id

                elif (line == 2):
                    match.goalsHome = td.getText().split(':')[0]
                    match.goalsAway = td.getText().split(':')[1].split()[0]
                    
                    if (match.goalsHome > match.goalsAway):
                        match.result = match.RESULT_HOME_WINNER
                    elif (match.goalsAway > match.goalsHome):
                        match.result = match.RESULT_AWAY_WINNER
                    else:
                        match.result = match.RESULT_DRAW

                elif (line == 3):
                    try:
                        match.oddHome = td['data-odd']
                    except:
                        match.oddHome = None

                elif (line == 4):
                    try:
                        match.oddDraw = td['data-odd']
                    except:
                        match.oddDraw = None

                elif (line == 5):
                    try:
                        match.oddAway = td['data-odd']
                    except:
                        match.oddAway = None

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
                        
def crawlerMatchFiles(matchId):

    url = "http://www.betexplorer.com//gres/ajax-matchodds.php"

    types = {'1x2', 'ou', 'ah', 'ha', 'dc', 'bts'}
    params = {} 
    params['t'] = 'n'
    params['e'] = matchId

    for tp in types:

        params['b'] = type
        fileName = path.BETEXPLORER_MATCHES  + matchId + "-" + tp + ".html"

        if (os.path.exists(fileName)):
            print("JA EXISTE: ", )
        else:
            r = requests.get(url,params=params)

            file = open(fileName,'wb')
            file.write(r.content)
            file.close()
                       
def extracTables():

    #list of championships
    championships = Championship.list()

    for champ in championships:
        
        print(champ)

        #list ID teams of championship
        teams = champ.listTeams()
        
        for team in teams:

            print(team)

            #list matches of team in championship order by match date
            matches = team.listMatches(champ.id)

            #var
            stats = dict(dict.fromkeys(['mp','mph','mpa','lml',\
                                        'w','d','l','gf','ga','p',\
                                        'wh','dh','lh','gfh','gah','ph',\
                                        'wa','da','la','gfa','gaa','pa'], 0))
            
            

            stats['lml'] = None
            print(stats)
            table = Table(champ.id, team.id, stats['lml'],\
                              stats['mp'],stats['w'],stats['d'],stats['l'],stats['gf'],stats['ga'],stats['p'],\
                              stats['mph'],stats['wh'],stats['dh'],stats['lh'],stats['gfh'],stats['gah'],stats['ph'],\
                              stats['mpa'],stats['wa'],stats['da'],stats['la'],stats['gfa'],stats['gaa'],stats['pa'])


            session.add(table)
            session.commit()
            
            for match in matches:


                table.nextMatchId = match.id
                session.commit()            

                if (match.homeTeamId == team.id):
                    
                    stats['mph']+=1 
                    
                    if (match.goalsHome > match.goalsAway):
                        stats['wh']+=1
                    elif (match.goalsHome < match.goalsAway):
                        stats['lh']+=1
                    else:
                        stats['dh']+=1

                    stats['gfh']+=match.goalsHome
                    stats['gah']+=match.goalsAway
                    stats['ph']= stats['wh']*3 + stats['dh']
                    stats['lml']= Table.LOCAL_HOME
                    
                else:

                    stats['mpa']+=1
                    
                    if (match.goalsAway > match.goalsHome):
                        stats['wa']+=1
                    elif (match.goalsAway < match.goalsHome):
                        stats['la']+=1
                    else:
                        stats['da']+=1
                        
                    stats['gfa']+=match.goalsAway
                    stats['gaa']+=match.goalsHome
                    stats['pa']= stats['wa']*3 + stats['da']
                    stats['lml']= Table.LOCAL_AWAY
            
                stats['w'] = stats['wh'] + stats['wa']
                stats['l'] = stats['lh'] + stats['la']
                stats['d'] = stats['dh'] + stats['da']
                stats['gf'] = stats['gfh'] + stats['gfa']
                stats['ga'] = stats['gah'] + stats['gaa']
                stats['p'] = stats['ph'] + stats['pa']
                stats['mp'] = stats['mph'] + stats['mpa']
                
                table = Table(champ.id, team.id, stats['lml'],\
                              stats['mp'],stats['w'],stats['d'],stats['l'],stats['gf'],stats['ga'],stats['p'],\
                              stats['mph'],stats['wh'],stats['dh'],stats['lh'],stats['gfh'],stats['gah'],stats['ph'],\
                              stats['mpa'],stats['wa'],stats['da'],stats['la'],stats['gfa'],stats['gaa'],stats['pa'])


                session.add(table)
                session.commit()
                
def extractEvalatuions():

    #list of championships
    matches = Match.list()

    for m in matches:
        
        try:
            evaluation = Evaluation()
            evaluation.matchId = m.id
            hit = False
            if (m.oddHome <= m.oddDraw):
                if (m.oddHome <= m.oddAway):
                    if (m.oddDraw <= m.oddAway): # H < D < A
                        tp = 'FMU'
                        if (m.result == 'H'):
                            hit = True
                    else: # H < A < D
                        tp = 'FUM'
                        if (m.result == 'H'):
                            hit = True
                else: # A < H < D
                    tp = 'MUF'
                    if (m.result == 'D'):
                        hit = True
            else: 
                if (m.oddHome <= m.oddAway): # H < A
                    tp = "MFU"
                    if (m.result == 'D'):
                        hit = True
                else: # A < H
                    if (m.oddDraw <= m.oddAway): # D < A < H
                        tp = 'UFM'
                        if (m.result == 'A'):
                            hit = True
                    else: # A < D < H
                        tp = 'UMF'
                        if (m.result == 'A'):
                            hit = True
                        
            evaluation.type = tp
            evaluation.hit_books = hit
            
            evaluation.save()
        except:
            pass
        
    session.commit()
        

        
        
        
                    
        
                
                
    

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

def updateMatches():
    
    #list of championships
    championships = Championship.list()

    for champ in championships:
        
        print(champ)

        #list ID teams of championship
        matches = champ.listMatches()
        
        if (len(matches) == 240):
            mn = 1
            mgn = 1 
            for m in matches:
                m.matchNum = mn
                m.matchGroupNum = mgn
                
                if (mn % 8 == 0):
                    mgn = mgn + 1
                
                mn = mn + 1
                
        session.commit()
                
            
updateMatches()