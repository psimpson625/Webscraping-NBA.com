#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 20 00:58:49 2021

@author: patricksimpson
"""

import requests
import json
import pandas as pd
from bs4 import BeautifulSoup as b4


from PIL import Image
from io import BytesIO

from urllib.request import Request, urlopen
req = Request('https://fullmatchtv.com/nba/philadelphia-76ers-vs-atlanta-hawks-18-06-21/', headers={'User-Agent': 'Mozilla/5.0'})



webpage = urlopen(req).read()
soup = b4(webpage.decode("utf-8"), "html.parser")

links = soup.find_all('iframe')

for link in links:
    if 'streamtape.com' in str(link):
        print(link['src']) #the streamtape link


#response = requests.get(link)
#img = Image.open(BytesIO(response.content))

#page = requests.get('https://www.nba.com/player/201142/rotowire')
#soup = b4(page.content, 'html.parser')

#soup.find('div', class_='cplayer-bio__content').get_text().replace("\'", "'")


#'https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/teamID/season/260x190/playerID.png'

# Gobert image:
#page = requests.get('https://www.nba.com/stats/player/203497/')
#soup = b4(page.content, 'html.parser')
#playerID = soup.find_all('img')[2]['player-id']
#teamID = soup.find_all('img')[2]['team-id']
#season = soup.find_all('img')[2]['season']
#link = 'https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/teamID/season/260x190/playerID.png'

#link=link.replace('teamID', teamID).replace('season', season).replace('playerID', playerID)



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



class Player:
    def __init__(self, name, season='2020-21', SeasonType = 'Regular Season'):
        self.name = name
        self.season = season
        self.SeasonType = SeasonType

    def __repr__(self):
        return f"Player({self.name}, {self.season} {self.SeasonType})"

    def id(self):
        pid = getDict().get(self.name)
        return pid

    def dashboard(self, MeasureType = 'Base'):
        pid = getDict().get(self.name)
        if self.SeasonType == 'Regular Season':
            s_type = 'Regular+Season'
        elif self.SeasonType == 'Playoffs':
            s_type = 'Playoffs'
        
        url_base = 'https://stats.nba.com/stats/playerdashboardbyyearoveryear?DateFrom=&DateTo=&GameSegment' \
                   '=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0' \
                   '&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerID='
        url_1 = '&PlusMinus=N&Rank=N&Season=2020-21&SeasonSegment=&SeasonType='
        url_2 = '&ShotClockRange=&Split=yoy&VsConference=&VsDivision='
        url = url_base + str(pid) + url_1 + s_type + url_2
        if MeasureType == 'Advanced':
            url = url.replace('MeasureType=Base', 'MeasureType=Advanced')
        elif MeasureType == 'Usage':
            url = url.replace('MeasureType=Base', 'MeasureType=Usage')
        elif MeasureType == 'Misc':
            url = url.replace('MeasureType=Base', 'MeasureType=Misc')
        elif MeasureType == 'Scoring':
            url = url.replace('MeasureType=Base', 'MeasureType=Scoring')
        page=requests.get(url, headers=headers)
        col_names=page.json()['resultSets'][1]['headers']
        data=page.json()['resultSets'][1]['rowSet']
        df=pd.DataFrame(data,columns=col_names)
        df['PlayerName']=self.name #Creating column for full name
        df.drop(['GROUP_SET','CFPARAMS'], inplace=True, axis=1) #dropping unnecessary columns
        #Reordering columns-want PlayerName to be first
        cols=df.columns.tolist()
        cols=cols[-1:]+cols[:-1]
        df=df[cols]
        return df

    def shotchart(self):
        pid = getDict().get(self.name)
        baseurl = 'https://stats.nba.com/stats/shotchartdetail?AheadBehind=&CFID=33&CFPARAMS='
        securl = '&ClutchTime=&Conference=&ContextFilter=&ContextMeasure=FGA&DateFrom=&DateTo=&Division=&EndPeriod=10' \
                 '&EndRange=28800&GROUP_ID=&GameEventID=&GameID=&GameSegment=&GroupID=&GroupMode=&GroupQuantity=5' \
                 '&LastNGames=0&LeagueID=00&Location=&Month=0&OnOff=&OpponentTeamID=0&Outcome=&PORound=0&Period=0' \
                 '&PlayerID='
        thirdurl = '&PlayerID1=&PlayerID2=&PlayerID3=&PlayerID4=&PlayerID5=&PlayerPosition=&PointDiff=&Position' \
                   '=&RangeType=0&RookieYear=&Season='
        endurl = '&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StartPeriod=1&StartRange=0&StarterBench' \
                 '=&TeamID=0&VsConference=&VsDivision=&VsPlayerID1=&VsPlayerID2=&VsPlayerID3=&VsPlayerID4' \
                 '=&VsPlayerID5=&VsTeamID='
        url = baseurl + str(self.season) + securl + str(pid) + thirdurl + str(self.season) + endurl
        if self.SeasonType == 'Playoffs':
            url = url.replace('&SeasonType=Regular+Season', '&SeasonType=Playoffs')
        elif self.SeasonType == 'PlayIn':
            url = url.replace('&SeasonType=Regular+Season', '&SeasonType=PlayIn')
        elif self.SeasonType == 'PreSeason':
            url = url.replace('&SeasonType=Regular+Season', '&SeasonType=Pre+Season')
        page=requests.get(url, headers=headers)
        col_names=page.json()['resultSets'][0]['headers']
        data=page.json()['resultSets'][0]['rowSet']
        df=pd.DataFrame(data,columns=col_names)
        return df
    
    def bio(self):
        pid = getDict().get(self.name)
        url = 'https://www.nba.com/player/ID/rotowire'
        url = url.replace('ID', str(pid))
        page = requests.get(url)
        soup = b4(page.content, 'html.parser')
        bio = soup.find('div', class_='cplayer-bio__content').get_text().replace("\'", "'")
        return bio
    
    def headshot(self):
        pid = getDict().get(self.name)
        general_link = 'https://www.nba.com/stats/player/pid/'
        general_link = general_link.replace('pid', str(pid))
        page = requests.get(general_link)
        soup = b4(page.content, 'html.parser')
        playerID = soup.find_all('img')[2]['player-id']
        teamID = soup.find_all('img')[2]['team-id']
        season = soup.find_all('img')[2]['season']
        link = 'https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/teamID/season/260x190/playerID.png'
        link=link.replace('teamID', teamID).replace('season', season).replace('playerID', playerID)
        response = requests.get(link)
        return Image.open(BytesIO(response.content))






#Getting all nba players in league history
def getPlayers():
    playerurl='https://stats.nba.com/stats/playerindex?College=&Country=&DraftPick=&DraftRound=&DraftYear=&Height=&Historical=1&LeagueID=00&Season=2020-21&SeasonType=Regular%20Season&TeamID=0&Weight='
    page=requests.get(playerurl, headers=headers)   
    col_names=page.json()['resultSets'][0]['headers']
    data=page.json()['resultSets'][0]['rowSet']
    df=pd.DataFrame(data,columns=col_names)
    df['PlayerName']=df['PLAYER_FIRST_NAME']+' '+df['PLAYER_LAST_NAME']
    return df
    
    
# Creating a dictionary for player name/ID:
def getDict():
    playerDF=getPlayers() #Getting all players
    lookup=dict(zip(playerDF['PlayerName'], playerDF['PERSON_ID'])) #our dictionary
    return(lookup)


#Getting NBA players for given season
def Players(Season):
    allplayers=getPlayers() #getting all players
    allplayers['FROM_YEAR']=allplayers['FROM_YEAR'].astype(int) #Want from year to be int
    allplayers['TO_YEAR']=allplayers['TO_YEAR'].astype(int) #Want to year to be int
    df=allplayers[(allplayers['TO_YEAR']>=int(Season[0:4])) & (allplayers['FROM_YEAR']<=int(Season[0:4]))]
    return(df)




#Getting Regular Season Standings for given season
def Standings(Season):
    urlbase='https://stats.nba.com/stats/leaguestandingsv3?LeagueID=00&Season='
    urlend='&SeasonType=Regular%20Season'
    url=urlbase+Season+urlend
    page=requests.get(url, headers=headers)
    col_names=page.json()['resultSets'][0]['headers']
    data=page.json()['resultSets'][0]['rowSet']
    standings=pd.DataFrame(data,columns=col_names)
    standings.drop('LeagueID', inplace=True, axis=1) #Dropping LeagueID
    standings['SeasonID']=standings['SeasonID'].replace([standings.iat[0,0]], Season)
    stand_new=standings.rename(columns={'SeasonID': 'Season'}, index={'ONE': 'Row_1'}) #Changing SeasonID column name to Season
    
    return(stand_new)



# Function to get opponent in Box Score data
def Opp(row):
    if len(row['MATCHUP'])==11:
        value=row['MATCHUP'][8:11]
    else:
        value=row['MATCHUP'][6:9]
    return value


#Player Box Scores for given season
def BoxScores(Season):
    urlbase='https://stats.nba.com/stats/leaguegamelog?Counter=1000&DateFrom=&DateTo=&Direction=DESC&LeagueID=00&PlayerOrTeam=P&Season='
    urlremainder='&SeasonType=Regular+Season&Sorter=DATE'
    playerurl=urlbase+Season+urlremainder
    page=requests.get(playerurl, headers=headers) 
    col_names=page.json()['resultSets'][0]['headers']
    data=page.json()['resultSets'][0]['rowSet']
    boxscores=pd.DataFrame(data,columns=col_names)
    boxscores.drop('VIDEO_AVAILABLE', inplace=True, axis=1) #Dropping LeagueID
    boxscores['SEASON_ID']=boxscores['SEASON_ID'].replace([boxscores.iat[0,0]], Season) #Changing SeasonID to Season Year
    df_new=boxscores.rename(columns={'SEASON_ID': 'Season'}, index={'ONE': 'Row_1'}) #Changing SeasonID column name to Season
    df_new['Opp']=df_new.apply(Opp, axis=1) #Getting Opponent
    return(df_new)
    
    


#Getting stat dashboard for player:
def PlayerDashboard(playerName):
    playerID=getDict().get(playerName)
    urlbase='https://stats.nba.com/stats/playerdashboardbyyearoveryear?DateFrom=&DateTo=&GameSegment=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerID='
    urlend='&PlusMinus=N&Rank=N&Season=2020-21&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&Split=yoy&VsConference=&VsDivision='
    url=urlbase+str(playerID)+urlend
    #page=requests.get(url, headers=headers)
    page=requests.get(url, headers=headers)
    col_names=page.json()['resultSets'][1]['headers']
    data=page.json()['resultSets'][1]['rowSet']
    df=pd.DataFrame(data,columns=col_names)
    df['PlayerName']=playerName #Creating column for full name
    df.drop(['GROUP_SET','CFPARAMS'], inplace=True, axis=1) #dropping unnecessary columns
    #Reordering columns-want PlayerName to be first
    cols=df.columns.tolist()
    cols=cols[-1:]+cols[:-1]
    df=df[cols]
    return df
    

# Location and outcome of each shot for a given season
def ShotChart(Season):
    import time
    StartTime=time.time()
    print('Getting Player Shot Location for '+Season)
    s=requests.Session()
    s.headers['User-Agent']='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
    #First need to get player ids:
    playerIDs=list(Players(Season)['PERSON_ID']) 
    baseurl='https://stats.nba.com/stats/shotchartdetail?AheadBehind=&CFID=33&CFPARAMS='
    securl='&ClutchTime=&Conference=&ContextFilter=&ContextMeasure=FGA&DateFrom=&DateTo=&Division=&EndPeriod=10&EndRange=28800&GROUP_ID=&GameEventID=&GameID=&GameSegment=&GroupID=&GroupMode=&GroupQuantity=5&LastNGames=0&LeagueID=00&Location=&Month=0&OnOff=&OpponentTeamID=0&Outcome=&PORound=0&Period=0&PlayerID='
    thirdurl='&PlayerID1=&PlayerID2=&PlayerID3=&PlayerID4=&PlayerID5=&PlayerPosition=&PointDiff=&Position=&RangeType=0&RookieYear=&Season='
    endurl='&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StartPeriod=1&StartRange=0&StarterBench=&TeamID=0&VsConference=&VsDivision=&VsPlayerID1=&VsPlayerID2=&VsPlayerID3=&VsPlayerID4=&VsPlayerID5=&VsTeamID='
    for player in playerIDs:
        try:
            url=baseurl+str(Season)+securl+str(player)+thirdurl+str(Season)+endurl
            time.sleep(.2)
            page=s.get(url, headers=headers, timeout=5)
            col_names=page.json()['resultSets'][0]['headers']
            data=page.json()['resultSets'][0]['rowSet']
            df=pd.DataFrame(data,columns=col_names)
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




    


def shot(season):
    import time
    StartTime=time.time()
    players = list(Players(season)['PlayerName']) #List of players for season
    for player in players:
        print('Getting shots for ' + player)
        try:
            df = Player(player).shotchart()
            time.sleep(.20)
            if player == players[0]:
                finalDF = df
            else:
                finalDF = finalDF.append(df)
        
        except requests.exceptions.Timeout:
            print('There was a connection error for '+player)
            time.sleep(10)
            players.insert(players.index(player), player)
            continue
        
        except json.JSONDecodeError:
            print('There was a json error for '+player)
            time.sleep(10)
            players.insert(players.index(player), player)
            continue
        
        except ValueError:
            continue
            
    executionTime = (time.time() - StartTime) #seconds
    import math
    executionMin=math.floor(executionTime/60)
    executionSec=round(executionTime-(executionMin*60),0)
    print('Execution time: ' + str(executionMin)+' Minutes and '+str(executionSec)+ ' Seconds.')
    return finalDF
            
        






def getAllDashboards():
    import time
    StartTime=time.time()
    playerList=getPlayers() #getting all players
    playerList['ToYear']=playerList['ToYear'].astype(int) #will use retirement year as filter
    playerList=playerList[playerList['ToYear']>=1996].PlayerName.tolist() #only want players who played post 1996
    
    for player in playerList:
        playersleft=len(playerList)-1-playerList.index(player)
        print('There are '+str(playersleft)+' players left to go')
        try:
            time.sleep(.25)
            df=PlayerDashboard(player)
            if player==playerList[0]:     
                dfFinal=PlayerDashboard(player)
            else:
                dfFinal=dfFinal.append(df)
            
        except requests.exceptions.Timeout:
            print('There was a connection error for '+player)
            time.sleep(10)
            playerList.insert(playerList.index(player), player)
            continue
        except ValueError:
            continue
        
    executionTime = (time.time() - StartTime) #seconds
    import math
    executionMin=math.floor(executionTime/60)
    executionSec=round(executionTime-(executionMin*60),0)
    print('Execution time: ' + str(executionMin)+' Minutes and '+str(executionSec)+ ' Seconds.')
    
    return(dfFinal)


#Getting player box scores dating back to 1996:
def getAllBoxscores():
    import time
    StartTime=time.time()
    year=2020
    while year>1995:
        print('Getting boxscores for '+str(year)+'-'+str(year+1)[2:4])
        df=BoxScores(str(year)+'-'+str(year+1)[2:4])
        if year==2020:
            dfFinal=df
        else:
            dfFinal=dfFinal.append(df)
        year=year-1  
    
    executionTime = (time.time() - StartTime) #seconds
    import math
    executionMin=math.floor(executionTime/60)
    executionSec=round(executionTime-(executionMin*60),0)
    print('Execution time: ' + str(executionMin)+' Minutes and '+str(executionSec)+ ' Seconds.')
        
    return(dfFinal)
        
    
    

