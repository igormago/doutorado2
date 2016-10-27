'''
Created on 30 de set de 2016

@author: igormago
'''
from sqlalchemy import Column, Integer, Numeric, String, Boolean, Date, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import case, distinct, or_
from mpmath import mp

Base = declarative_base()

engine = create_engine('mysql+mysqlconnector://root:root@localhost/doutorado_explorer')
Session = sessionmaker(bind=engine)
session = Session()

def getSession():
    return session

def getEngine():
    return engine

class ModelMixin(object):

    def save(self):
        session.add(self)

    @classmethod
    def list(cls):
        return session.query(cls).filter().all()

    def __init__(self,*args,**kwargs):
        pass

class Championship(Base,ModelMixin):
    __tablename__ = 'championships'

    id = Column("championship_id",Integer, primary_key=True, autoincrement=True)
    name = Column("championship_name",String(100))
    year = Column(Integer)

    def __repr__(self):
        r = "Championship: ", self.id, self.name, self.year
        return (str(r))

    @staticmethod
    def get (championshipName, year):
        return session.query(Championship).filter(Championship.name == championshipName,
                                                  Championship.year == year).one()

    @staticmethod
    def getById (champId):
        return session.query(Championship).filter(Championship.id == champId).one()
                                                  
    def listMatches (self):
        return session.query(Match).filter(Match.championshipId == self.id).order_by(Match.matchDate).all()
    
    def getFileName(self):
        return self.name + "-" + str(self.year) + ".html"
    
    def listTeams(self):
        return session.query(Team).filter(or_(Match.awayTeamId == Team.id, Match.homeTeamId == Team.id),\
                                                        Match.championshipId == self.id).distinct().all()
                                                        

class Team(Base, ModelMixin):
    __tablename__ = 'teams'

    id = Column ('team_id',Integer, primary_key=True, autoincrement=True )
    name = Column('team_name',String(45))

    def __repr__(self):
        r = "Team: ", self.id, self.name
        return (str(r))

    def get(self,teamName):
        return session.query(Team).filter(Team.name == teamName).one()

    def getById(self, teamId):
        return session.query(Team).filter(Team.id == teamId).one()
    
    def listMatches(self, championshipId):
        return session.query(Match).filter(or_(Match.awayTeamId == self.id, Match.homeTeamId == self.id),\
                                                  Match.championshipId == championshipId).order_by(Match.matchDate).all()

class Match(Base,ModelMixin):

    __tablename__ = 'matches'
    
    RESULT_HOME_WINNER = 'H'
    RESULT_DRAW = 'D'
    RESULT_AWAY_WINNER ='A'

    id = Column("match_id",String(45), primary_key=True)
    championshipId = Column("championship_id",Integer, ForeignKey('championships.championship_id'))
    homeTeamId = Column("home_team_id", Integer, ForeignKey('teams.team_id'))
    awayTeamId = Column("away_team_id", Integer,ForeignKey('teams.team_id'))
    goalsHome = Column("goals_home", Integer)
    goalsAway = Column("goals_away", Integer)
    result = Column("column_result",String(1))
    matchDate = Column("match_date",Date)
    roundNum = Column("round_num",Integer)
    oddsHome = Column("odds_home",Numeric)
    oddsDraw = Column("odds_draw",Numeric)
    oddsAway = Column("odds_away",Numeric)

    def __repr__(self):
        return "ID: " + self.id  + ": " + str(self.homeTeamId) +\
        "(" + str(self.goalsHome) + ") x (" + str(self.goalsAway) + ")" + str(self.awayTeamId)

    @staticmethod
    def get (matchId):
        return session.query(Match).filter(Match.id==matchId).one()

    def getFileName(self, oddType):
        return self.id + "_" + oddType + ".html"
    
    @staticmethod
    def list ():
        return session.query(Match).filter().all()

    def favorite (self):
        if (self.oddsHome <= self.oddsDraw and self.oddsHome <= self.oddsAway):
            return Match.RESULT_HOME_WINNER;
        elif(self.oddsDraw <= self.oddsAway):
            return Match.RESULT_DRAW;
        return Match.RESULT_AWAY_WINNER;

    def favorite_odd (self):
        if (self.oddsHome <= self.oddsDraw and self.oddsHome <= self.oddsAway):
            return self.oddsHome;
        elif(self.oddsDraw <= self.oddsAway):
            return self.oddsDraw;
        return self.oddsAway;

    def medium_odd (self):
        if (self.oddsHome <= self.oddsDraw and self.oddsHome <= self.oddsAway):
            if(self.oddsDraw <= self.oddsAway):
                return self.oddsDraw
            else:
                return self.oddsAway
        elif (self.oddsHome >= self.oddsDraw and self.oddsHome >= self.oddsAway):
            if (self.oddsDraw <= self.oddsAway):
                return self.oddsAway
            else:
                return self.oddsDraw
        else:
            return self.oddsHome

    def underdog_odd (self):
        if (self.oddsHome >= self.oddsDraw and self.oddsHome >= self.oddsAway):
            return self.oddsHome
        elif(self.oddsDraw <= self.oddsAway):
            return self.oddsAway
        return self.oddsDraw

    @hybrid_property
    def result_odd(self):
        if (self.result == Match.RESULT_HOME_WINNER):
            return self.oddsHome
        elif (self.result == Match.RESULT_DRAW):
            return self.oddsDraw
        else:
            return self.oddsAway

    @result_odd.expression
    def type(self, cls):
        return case({cls.result == 0: cls.oddsHome, cls.result == 1: cls.oddsDraw, cls.result == 2: cls.oddsAway})

    def result_fmu(self):

        if (self.result == Match.RESULT_HOME_WINNER):
            if (self.oddsHome <= self.oddsDraw and self.oddsHome <= self.oddsAway):
                return 'F'
            elif  (self.oddsHome >= self.oddsDraw and self.oddsHome >= self.oddsAway):
                return 'U'
            else:
                return 'M'
        elif (self.result == Match.RESULT_DRAW):
            if (self.oddsDraw <= self.oddsHome and self.oddsDraw <= self.oddsAway):
                return 'F'
            elif (self.oddsDraw >= self.oddsHome and self.oddsDraw >= self.oddsAway):
                return 'U'
            else:
                return 'M'
        else:
            if (self.oddsAway <= self.oddsHome and self.oddsAway <= self.oddsDraw):
                return 'F'
            elif (self.oddsAway >= self.oddsHome and self.oddsAway >= self.oddsDraw):
                return 'U'
            else:
                return 'M'


class Bookmaker(Base,ModelMixin):

    __tablename__ = 'bookmakers'

    id = Column("bookmaker_id",Integer, primary_key=True, autoincrement=True)
    name = Column("bookmaker_name",String(45), unique=True)

    def __repr__(self):
        return "ID: " + str(self.id) + ",NAME: " + self.name

    @staticmethod
    def get (bookmakerName):
        return session.query(Bookmaker).filter(Bookmaker.name == bookmakerName).one()

    @staticmethod
    def list (self):
        return session.query(Bookmaker).filter().all()

class Odds(Base,ModelMixin):

    __tablename__ = 'odds'

    matchId = Column("match_id",String(45), ForeignKey('matches.match_id'), primary_key=True)
    bookmakerId = Column("bookmaker_id",Integer, ForeignKey('bookmakers.bookmaker_id'), primary_key=True)
    oddsHome = Column("odds_home",Numeric)
    oddsDraw = Column("odds_draw",Numeric)
    oddsAway = Column("odds_away",Numeric)

    @staticmethod
    def get (matchId, bookmakerId):
        return session.query(Odds).filter(Odds.matchId==matchId,Odds.bookmakerId==bookmakerId).one()
    
    @staticmethod
    def list(matchId):
        return session.query(Odds).filter(Odds.matchId==matchId).all()

class OddsOU(Base,ModelMixin):

    __tablename__ = 'odds_OU'

    matchId = Column("match_id",String(45), ForeignKey('matches.match_id'), primary_key=True)
    bookmakerId = Column("bookmaker_id",Integer, ForeignKey('bookmakers.bookmaker_id'), primary_key=True)
    goals = Column("goals_num",Numeric,primary_key=True)
    oddsOver = Column("odds_over",Numeric)
    oddsUnder = Column("odds_under",Numeric)

    @staticmethod
    def get (matchId, bookmakerId, goals):
        return session.query(OddsOU).filter(OddsOU.matchId==matchId,OddsOU.bookmakerId==bookmakerId,\
                                            OddsOU.goals==goals).one()
    @staticmethod
    def list(matchId):
        return session.query(OddsOU).filter(OddsOU.matchId==matchId).all()

class OddsAH(Base,ModelMixin):

    __tablename__ = 'odds_AH'

    matchId = Column("match_id",String(45), ForeignKey('matches.match_id'), primary_key=True)
    bookmakerId = Column("bookmaker_id",Integer, ForeignKey('bookmakers.bookmaker_id'), primary_key=True)
    handicap = Column("handicap",String(45), primary_key=True)
    oddsHome = Column("odds_home",Numeric)
    oddsAway = Column("odds_away",Numeric)

    @staticmethod
    def get (matchId, bookmakerId, handicap):
        return session.query(OddsAH).filter(OddsAH.matchId==matchId,OddsAH.bookmakerId==bookmakerId,\
                                            OddsAH.handicap==handicap).one()

    @staticmethod
    def list( matchId):
        return session.query(OddsAH).filter(OddsAH.matchId==matchId).all()

class OddsDC(Base,ModelMixin):

    __tablename__ = 'odds_DC'

    matchId = Column("match_id",String(45), ForeignKey('matches.match_id'), primary_key=True)
    bookmakerId = Column("bookmaker_id",Integer, ForeignKey('bookmakers.bookmaker_id'), primary_key=True)
    oddsHomeDraw = Column("odds_home_draw",Numeric)
    oddsHomeAway = Column("odds_home_away",Numeric)
    oddsAwayDraw = Column("odds_away_draw",Numeric)

    @staticmethod
    def get (matchId, bookmakerId):
        return session.query(OddsDC).filter(OddsDC.matchId==matchId,OddsDC.bookmakerId==bookmakerId).one()

    @staticmethod
    def list(matchId):
        return session.query(OddsDC).filter(OddsDC.matchId==matchId).all()

class OddsDNB(Base,ModelMixin):

    __tablename__ = 'odds_DNB'

    matchId = Column("match_id",String(45), ForeignKey('matches.match_id'), primary_key=True)
    bookmakerId = Column("bookmaker_id",Integer, ForeignKey('bookmakers.bookmaker_id'), primary_key=True)
    oddsHome = Column("odds_home",Numeric)
    oddsAway = Column("odds_away",Numeric)

    @staticmethod
    def get (matchId, bookmakerId):
        return session.query(OddsDNB).filter(OddsDNB.matchId==matchId,OddsDNB.bookmakerId==bookmakerId).one()

    @staticmethod
    def list(matchId):
        return session.query(OddsDNB).filter(OddsDNB.matchId==matchId).all()

class OddsBTS(Base,ModelMixin):

    __tablename__ = 'odds_BTS'

    matchId = Column("match_id",String(45), ForeignKey('matches.match_id'), primary_key=True)
    bookmakerId = Column("bookmaker_id",Integer, ForeignKey('bookmakers.bookmaker_id'), primary_key=True)
    oddsYes = Column("odds_yes",Numeric)
    oddsNo = Column("odds_no",Numeric)

    @staticmethod
    def get (matchId, bookmakerId):
        return session.query(OddsBTS).filter(OddsBTS.matchId==matchId,OddsBTS.bookmakerId==bookmakerId).one()

    @staticmethod
    def list(matchId):
        return session.query(OddsBTS).filter(OddsBTS.matchId==matchId).all()

class Ranking(Base):

    __tablename__ = 'ranking'
    matchId = Column("match_id",String(45),ForeignKey('matches.match_id'),primary_key=True)
    teamId = Column("team_id",Integer,ForeignKey('teams.team_id'),primary_key=True)
    local = Column("local",String(1),primary_key=True)
    matchesPlayed = Column("matches_played",Integer,primary_key=True)
    lastMatchesNum = Column("last_matches_num",Integer,primary_key=True)
    winners = Column(String)
    draws = Column(Integer)
    loses = Column(Integer)
    goalsFor = Column("goals_for",Integer)
    goalsAgainst = Column("goals_against",Integer)
    points = Column("points", Integer)

    def __repr__(self):
        r =  self.matchId, self.teamId, self.local, self.matchesPlayed, self.lastMatchesNum,\
                self.winners, self.draws, self.loses, self.goalsFor, self.goalsAgainst, self.points
        return str(r)

    def list(self):
        return session.query(Ranking).all()

    def getPointsAvg(self):
        gaa = 0
        try:
            gaa = self.points / self.lastMatchesNum
        except:
            pass

        return gaa

    def getGoalsForAvg(self):
        gfa = 0
        try:
            gfa = self.goalsFor / self.lastMatchesNum
        except:
            pass

        return gfa

    def getGoalsAgainstAvg(self):
        gaa = 0
        try:
            gaa = self.goalsAgainst / self.lastMatchesNum
        except:
            pass

        return gaa

    def getGoalsDifference(self):
        return self.goalsFor - self.goalsAgainst

class Bet(Base):

    __tablename__ = 'bet_match'
    matchId = Column("match_id",String(45),ForeignKey('matches.match_id'),primary_key=True)
    criterion = Column("criterion", String(45), primary_key=True)
    lastMatchesNum = Column("last_matches_num",Integer,primary_key=True)
    local = Column(Boolean,primary_key=True)
    betColumn = Column("bet_column",Integer)
    hit = Column(Boolean)

    def __repr__(self):
        return "(ID: " + self.matchId + ", MATCHES: " + str(self.lastMatchesNum) + ", LOCAL: " +\
         str(self.local) + ", BET: " + str(self.betColumn) +  ", HIT: " + str(self.hit) +')'

    def list(self):
        return session.query(Bet).filter().all()

class ResumeOdds (Base,ModelMixin):

    __tablename__ = 'resume_odds'

    matchId = Column("match_id",String(45),ForeignKey('matches.match_id'),primary_key=True)
    avgHome = Column("avg_home",Numeric)
    avgDraw = Column("avg_draw",Numeric)
    avgAway = Column("avg_away",Numeric)
    maxHome = Column("max_home",Numeric)
    maxDraw = Column("max_draw",Numeric)
    maxAway = Column("max_away",Numeric)
    minHome = Column("min_home",Numeric)
    minDraw = Column("min_draw",Numeric)
    minAway = Column("min_away",Numeric)
    count = Column("count",Integer)

    @staticmethod
    def get (matchId):
        return session.query(ResumeOdds).filter(ResumeOdds.matchId==matchId).one()

    @staticmethod
    def list():
        return session.query(ResumeOdds).filter().all()

class ResumeOddsBTS (Base,ModelMixin):

    __tablename__ = 'resume_odds_BTS'

    matchId = Column("match_id",String(45),ForeignKey('matches.match_id'),primary_key=True)
    avgYes = Column("avg_yes",Numeric)
    avgNo = Column("avg_no",Numeric)
    maxYes = Column("max_yes",Numeric)
    maxNo = Column("max_no",Numeric)
    minYes = Column("min_yes",Numeric)
    minNo = Column("min_no",Numeric)
    count = Column("count",Integer)

    def get (self, matchId):
        return session.query(ResumeOddsBTS).filter(ResumeOddsBTS.matchId==matchId).one()

    def list(self):
        return session.query(ResumeOddsBTS).filter().all()


class ResumeOddsOU (Base,ModelMixin):

    __tablename__ = 'resume_odds_OU'

    matchId = Column("match_id",String(45),ForeignKey('matches.match_id'),primary_key=True)
    goals = Column("goals_num",Integer,primary_key=True)
    avgOver = Column("avg_over",Numeric)
    avgUnder = Column("avg_under",Numeric)
    maxOver = Column("max_over",Numeric)
    maxUnder = Column("max_under",Numeric)
    minOver = Column("min_over",Numeric)
    minUnder = Column("min_under",Numeric)
    count = Column("count",Integer)

    def get (self,matchId, goals):
        return session.query(ResumeOddsOU).filter(ResumeOddsOU.matchId==matchId, ResumeOddsOU.goals==goals).one()

    def listByMatch (self,matchId):
        return session.query(ResumeOddsOU).filter(ResumeOddsOU.matchId==matchId).all()

    def list (self):
        return session.query(ResumeOddsOU).filter().all()

class ResumeOddsAH (Base,ModelMixin):

    __tablename__ = 'resume_odds_AH'

    matchId = Column("match_id",String(45),ForeignKey('matches.match_id'),primary_key=True)
    handicap = Column("handicap",String(45),primary_key=True)
    avgHome = Column("avg_home",Numeric)
    avgAway = Column("avg_away",Numeric)
    maxHome = Column("max_home",Numeric)
    maxAway = Column("max_away",Numeric)
    minHome = Column("min_home",Numeric)
    minAway = Column("min_away",Numeric)
    count = Column("count",Integer)

    def get (self,matchId, handicap):
        return session.query(ResumeOddsAH).filter(ResumeOddsAH.matchId==matchId, ResumeOddsAH.handicap==handicap).one()

    def listByMatch (self,matchId):
        return session.query(ResumeOddsAH).filter(ResumeOddsAH.matchId==matchId).all()

class ResumeOddsDNB (Base,ModelMixin):

    __tablename__ = 'resume_odds_DNB'

    matchId = Column("match_id",String(45),ForeignKey('matches.match_id'),primary_key=True)
    avgHome = Column("avg_home",Numeric)
    avgAway = Column("avg_away",Numeric)
    maxHome = Column("max_home",Numeric)
    maxAway = Column("max_away",Numeric)
    minHome = Column("min_home",Numeric)
    minAway = Column("min_away",Numeric)
    count = Column("count",Integer)

    def get (self, matchId):
        return session.query(ResumeOddsDNB).filter(ResumeOddsDNB.matchId==matchId).one()

class ResumeOddsDC (Base,ModelMixin):

    __tablename__ = 'resume_odds_DC'

    matchId = Column("match_id",String(45),ForeignKey('matches.match_id'),primary_key=True)
    avgHomeAway = Column("avg_home_away",Numeric)
    avgHomeDraw= Column("avg_home_draw",Numeric)
    avgAwayDraw = Column("avg_away_draw",Numeric)
    maxHomeDraw = Column("max_home_draw",Numeric)
    maxHomeAway = Column("max_home_away",Numeric)
    maxAwayDraw = Column("max_away_draw",Numeric)
    minHomeDraw = Column("min_home_draw",Numeric)
    minHomeAway = Column("min_home_away",Numeric)
    minAwayDraw = Column("min_away_draw",Numeric)
    count = Column("count",Integer)

    def get (self, matchId):
        return session.query(ResumeOddsDC).filter(ResumeOddsDC.matchId==matchId).one()
    
class Table(Base, ModelMixin):
    
    LOCAL_HOME = 'H'
    LOCAL_AWAY = 'A'

    __tablename__ = 'tables'
    championshipId = Column("championship_id",Integer,ForeignKey('championships.championship_id'),primary_key=True)
    teamId = Column("team_id",Integer,ForeignKey('teams.team_id'),primary_key=True)
    matchesPlayed = Column("matches_played",Integer,primary_key=True)
    winners = Column("winners",String)
    draws = Column("draws",Integer)
    loses = Column("loses",Integer)
    goalsFor = Column("goals_for",Integer)
    goalsAgainst = Column("goals_against",Integer)
    points = Column("points", Integer)
    matchesPlayedHome = Column("matches_played_home",Integer)
    winnersHome = Column("winners_home",String)
    drawsHome = Column("draws_home",Integer)
    losesHome = Column("loses_home",Integer)
    goalsForHome = Column("goals_for_home",Integer)
    goalsAgainstHome = Column("goals_against_home",Integer)
    pointsHome = Column("points_home", Integer)
    matchesPlayedAway = Column("matches_played_away",Integer)
    winnersAway = Column("winners_away",String)
    drawsAway = Column("draws_away",Integer)
    losesAway = Column("loses_away",Integer)
    goalsForAway = Column("goals_for_away",Integer)
    goalsAgainstAway = Column("goals_against_away",Integer)
    pointsAway = Column("points_away", Integer)
    lastMatchLocal = Column("last_match_local",String(1))
    nextMachId = Column("next_match_id", String(45),ForeignKey('matches.match_id'))

    def __init__(self, champId, teamId, lastMatchLocal,\
                 matchesPlayed,winners,draws,loses,goalsFor,goalsAgainst,points,\
                 matchesPlayedHome,winnersHome,drawsHome,losesHome,goalsForHome,goalsAgainstHome,pointsHome,\
                 matchesPlayedAway,winnersAway,drawsAway,losesAway,goalsForAway,goalsAgainstAway,pointsAway
                 ):
        
        self.championshipId = champId
        self.teamId = teamId
        self.lastMatchLocal = lastMatchLocal
        
        self.matchesPlayed = matchesPlayed
        self.winners = winners
        self.draws = draws
        self.loses = loses
        self.goalsFor= goalsFor
        self.goalsAgainst = goalsAgainst
        self.points = points 
        
        self.matchesPlayedHome = matchesPlayedHome
        self.winnersHome = winnersHome
        self.drawsHome = drawsHome
        self.losesHome = losesHome
        self.goalsForHome = goalsForHome
        self.goalsAgainstHome = goalsAgainstHome
        self.pointsHome = pointsHome
        
        self.matchesPlayedAway = matchesPlayedAway
        self.winnersAway = winnersAway
        self.drawsAway = drawsAway
        self.losesAway = losesAway
        self.goalsForAway = goalsForAway
        self.goalsAgainstAway = goalsAgainstAway
        self.pointsAway = pointsAway
        
    @staticmethod
    def getByMatch(matchId):
        
        return session.query(Table).filter(Table.nextMachId==matchId).all()
