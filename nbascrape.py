#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 21:06:20 2021

@author: patricksimpson
"""

from bs4 import BeautifulSoup
import requests
import json
import pandas as pd
import numpy as np


headers = {
		'Host': 'stats.nba.com',
		'Connection': 'keep-alive',
		'Accept': 'application/json, text/plain, */*',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
		'Referer': 'https://stats.nba.com/',
		"x-nba-stats-origin": "stats",
		"x-nba-stats-token": "true",
		'Accept-Encoding': 'gzip, deflate, br',
		'Accept-Language': 'en-US,en;q=0.9',
	}


#Getting all nba players in league history
def getPlayers():
    playerurl='https://stats.nba.com/stats/playerindex?College=&Country=&DraftPick=&DraftRound=&DraftYear=&Height=&Historical=1&LeagueID=00&Season=2020-21&SeasonType=Regular%20Season&TeamID=0&Weight='
    page=requests.get(playerurl, headers=headers)    
    content=page.text
    soup=BeautifulSoup(content)
    site_json=json.loads(soup.text)
    data=site_json['resultSets'][0]['rowSet']
    df=pd.DataFrame(data, columns=['PlayerID', 'LastName', 'FirstName', 'PlayerSlug',
                               'TeamID', 'TeamSlug', 'IsDefunct', 'TeamCity',
                               'TeamName', 'TeamAbb', 'JerseryNum', 'Position',
                               'Height', 'Weight', 'College', 'Country', 'DraftYear',
                               'DraftRound', 'DraftNumber', 'RosterStatus', 'Ppg',
                               'Rpg', 'Apg', 'StatsTimeFrame', 'FromYr', 'ToYear'])
    return(df)


# Creating a dictionary for player name/ID:
def getDict():
    playerDF=getPlayers() #Getting all players
    playerDF['Name']=playerDF['FirstName']+' '+playerDF['LastName'] #adding a column for full name
    lookup=dict(zip(playerDF['Name'], playerDF['PlayerID'])) #our dictionary
    return(lookup)


#Getting NBA players for given season
def Players(Season):
    allplayers=getPlayers() #getting all players
    allplayers['FromYr']=allplayers['FromYr'].astype(int) #Want from year to be int
    allplayers['ToYear']=allplayers['ToYear'].astype(int) #Want to year to be int
    df=allplayers[(allplayers['ToYear']>=int(Season[0:4])) & (allplayers['FromYr']<=int(Season[0:4]))]
    return(df)



#Getting Regular Season Standings for given season
def Standings(Season):
    urlbase='https://stats.nba.com/stats/leaguestandingsv3?LeagueID=00&Season='
    urlend='&SeasonType=Regular%20Season'
    url=urlbase+Season+urlend
    page=requests.get(url, headers=headers)    
    content=page.text
    soup=BeautifulSoup(content)
    site_json=json.loads(soup.text)
    data=site_json['resultSets'][0]['rowSet']
    df=pd.DataFrame(data, columns=['LeagueID', 'SeasonID', 'TeamID', 'TeamCity',
                                   'TeamName', 'TeamSlug', 'Conference', 'ConferenceRecord',
                                   'PlayoffRank', 'ClinchIndicator', 'Division', 'DivisionRecord',
                                   'DivisionRank', 'Wins', 'Losses', 'WinPCT',
                                   'LeagueRank', 'Record', 'Home', 'Road',
                                   'L10', 'Last10Home', 'Last10Road', 'OT',
                                   'ThreePtsOrLess', 'TenPtsOrMore', 'LongHomeStreak', 'strLongHomeStreak',
                                   'LongRoadStreak', 'strLongRoadStreak','LongWinStreak', 'LongLossStreak',
                                   'CurrentHomeStreak', 'strCurrentHomeStreak', 'CurrentRoadStreak', 'strCurrentRoadStreak',
                                   'CurrentStreak', 'strCurrentStreak', 'ConferenceGamesBack', 'DivisionGamesBack',
                                   'ClinchedConferenceTitle', 'ClinchedDivisionTitle', 'ClinchedPlayoffBirth', 'ClinchedPlayIn',
                                   'EliminatedConference', 'EliminatedDivision', 'AheadAtHalf', 'BehindAtHalf',
                                   'TiedAtHalf', 'AheadAtThird', 'BehindAtThird', 'TiedAtThird',
                                   'Score100Pts', 'OppScore100Pts', 'OppOver500', 'LeadInFgPct',
                                   'LeadInReb', 'FewerTurnovers', 'PPG', 'OPPG',
                                   'DiffPPG', 'vsEast', 'vsAtlantic', 'vsCentral',
                                   'vsSoutheast', 'vsWest', 'vsNorthwest', 'vsPacific',
                                   'vsSouthwest', 'Jan', 'Feb', 'Mar',
                                   'Apr', 'May', 'Jun', 'Jul',
                                   'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    df.drop('LeagueID', inplace=True, axis=1) #Dropping LeagueID
    df['SeasonID']=df['SeasonID'].replace([df.iat[0,0]], Season) #Changing SeasonID to Season Year
    df_new=df.rename(columns={'SeasonID': 'Season'}, index={'ONE': 'Row_1'}) #Changing SeasonID column name to Season
    return(df_new)



# Function to get opponent in Box Score data
def Opp(row):
    if len(row['Matchup'])==11:
        value=row['Matchup'][8:11]
    else:
        value=row['Matchup'][6:9]
    return value


#Player Box Scores for given season
def BoxScores(Season):
    urlbase='https://stats.nba.com/stats/leaguegamelog?Counter=1000&DateFrom=&DateTo=&Direction=DESC&LeagueID=00&PlayerOrTeam=P&Season='
    urlremainder='&SeasonType=Regular+Season&Sorter=DATE'
    playerurl=urlbase+Season+urlremainder
    page=requests.get(playerurl, headers=headers)    
    content=page.text
    soup=BeautifulSoup(content)
    site_json=json.loads(soup.text)
    data=site_json['resultSets'][0]['rowSet']
    df=pd.DataFrame(data, columns=['SeasonID', 'PlayerID', 'PlayerName', 'TeamID',
                               'Team', 'TeamName', 'GameID', 'GameDate',
                               'Matchup', 'WL', 'Min', 'Fgm',
                               'Fga', 'FgPct', 'Fg3m', 'Fg3a', 'Fg3Pct',
                               'Ftm', 'Fta', 'FtPct', 'Oreb',
                               'Dreb', 'Reb', 'Ast', 'Stl', 'Blk', 'Tov', 'Pf',
                               'Pts', 'PlusMinus', 'FanPts', 'VideoAv'])
    df.drop('VideoAv', inplace=True, axis=1) #Dropping LeagueID
    df['SeasonID']=df['SeasonID'].replace([df.iat[0,0]], Season) #Changing SeasonID to Season Year
    df_new=df.rename(columns={'SeasonID': 'Season'}, index={'ONE': 'Row_1'}) #Changing SeasonID column name to Season
    df_new['Opp']=df_new.apply(Opp, axis=1) #Getting Opponent
    newcolumns=['Season', 'PlayerID', 'PlayerName', 'TeamID',
                               'Team', 'Opp', 'TeamName', 'GameID', 'GameDate',
                               'Matchup', 'WL', 'Min', 'Fgm',
                               'Fga', 'FgPct', 'Fg3m', 'Fg3a', 'Fg3Pct',
                               'Ftm', 'Fta', 'FtPct', 'Oreb',
                               'Dreb', 'Reb', 'Ast', 'Stl', 'Blk', 'Tov', 'Pf',
                               'Pts', 'PlusMinus', 'FanPts']
    df_new=df_new.reindex(columns=newcolumns)
    return(df_new)



# Location and outcome of each shot for a given season
def ShotChart(Season):
    import time
    StartTime=time.time()
    print('Getting Player Shot Location for '+Season)
    s=requests.Session()
    columnNames=['GridType', 'GameID', 'GameEventID', 'PlayerID',
                                       'PlayerName', 'TeamID', 'TeamName', 'Period',
                                       'MinRem', 'SecRem', 'EventType', 'ActionType',
                                       'ShotType', 'ShotZoneBasic', 'ShotZoneArea', 'ShotZoneRange',
                                       'ShotDistance', 'LocX', 'LocY', 'ShotAttFlag', 'ShotMadeFlag',
                                       'GameDate', 'Home', 'Away']
    s.headers['User-Agent']='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
    #First need to get player ids:
    playerDF=Players(Season)
    playerIDs=list(playerDF['PlayerID']) #List of PlayerIDs
    baseurl='https://stats.nba.com/stats/shotchartdetail?AheadBehind=&CFID=33&CFPARAMS='
    securl='&ClutchTime=&Conference=&ContextFilter=&ContextMeasure=FGA&DateFrom=&DateTo=&Division=&EndPeriod=10&EndRange=28800&GROUP_ID=&GameEventID=&GameID=&GameSegment=&GroupID=&GroupMode=&GroupQuantity=5&LastNGames=0&LeagueID=00&Location=&Month=0&OnOff=&OpponentTeamID=0&Outcome=&PORound=0&Period=0&PlayerID='
    thirdurl='&PlayerID1=&PlayerID2=&PlayerID3=&PlayerID4=&PlayerID5=&PlayerPosition=&PointDiff=&Position=&RangeType=0&RookieYear=&Season='
    endurl='&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StartPeriod=1&StartRange=0&StarterBench=&TeamID=0&VsConference=&VsDivision=&VsPlayerID1=&VsPlayerID2=&VsPlayerID3=&VsPlayerID4=&VsPlayerID5=&VsTeamID='
    for player in playerIDs:
        try:
            url=baseurl+str(Season)+securl+str(player)+thirdurl+str(Season)+endurl
            time.sleep(.25)
            page=s.get(url, headers=headers, timeout=5)
            content=page.text
            soup=BeautifulSoup(content)
            site_json=json.loads(soup.text)
            data=site_json['resultSets'][0]['rowSet']
            df=pd.DataFrame(data, columns=columnNames)
            print('Obtained player shots for ID: '+str(player))
            if player==playerIDs[0]:
                dfFinal=df
            else:
                dfFinal=dfFinal.append(df)

        except requests.exceptions.Timeout:
            print('There was a connection error for '+str(player))
            time.sleep(10)
            playerIDs.insert(playerIDs.index(player), player)
            continue
    
    executionTime = (time.time() - StartTime) #seconds
    import math
    executionMin=math.floor(executionTime/60)
    executionSec=round(executionTime-(executionMin*60),0)
    
    print('Execution time: ' + str(executionMin)+' Minutes and '+str(executionSec)+ ' Seconds.')
    return(dfFinal)


#Getting stat dashboard for player:
def PlayerDashboard(playerName):
    lookup=getDict() #Getting dictionary to lookup PlayerID
    playerID=lookup.get(playerName)
    urlbase='https://stats.nba.com/stats/playerdashboardbyyearoveryear?DateFrom=&DateTo=&GameSegment=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerID='
    urlend='&PlusMinus=N&Rank=N&Season=2020-21&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&Split=yoy&VsConference=&VsDivision='
    url=urlbase+str(playerID)+urlend
    page=requests.get(url, headers=headers)
    content=page.text
    soup=BeautifulSoup(content)
    site_json=json.loads(soup.text)
    data=site_json['resultSets'][1]['rowSet']
    columnNames=['GroupSet', 'GroupValue', 'TeamID', 'TeamAbb', 'MaxGameDate',
                 'GP', 'W', 'L', 'W_PCT', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M',
                 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST',
                 'TOV', 'STL', 'BLK', 'BLKA', 'PF', 'PFD', 'PTS', 'PlusMinus',
                 'FanPts', 'DD2', 'TD3', 'GP_RANK', 'W_RANK', 'L_RANK', 'W_PCT_RANK',
                 'MIN_RANK', 'FGM_RANK', 'FGA_RANK', 'FG_PCT_RANK', 'FG3M_RANK',
                 'FG3A_RANK', 'FG3_PCT_RANK', 'FTM_RANK', 'FTA_RANK', 'FT_PCT_RANK',
                 'OREB_RANK', 'DREB_RANK', 'REB_RANK', 'AST_RANK', 'TOV_RANK', 'STL_RANK',
                 'BLK_RANK', 'BLKA_RANK', 'PF_RANK', 'PFD_RANK', 'PTS_RANK', 'PlusMinusRANK',
                 'FanPtsRank', 'DD2_RANK', 'TD3_RANK', 'CFID', 'CFPARAMS']
    df=pd.DataFrame(data, columns=columnNames)

    return(df)

    











