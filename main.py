import os
from collections import defaultdict

from yahoo_oauth import OAuth2
# Import packages
import xml.etree.ElementTree as ET
import re
import csv

# Thanks to https://www.billyboyballin.com/2019/08/18/yahoo-fantasy-api/

oauth = OAuth2(None, None, from_file='oauth.json')
if not oauth.token_is_valid():
    oauth.refresh_access_token()

print(oauth)


# url = "https://fantasysports.yahooapis.com/fantasy/v2/leagues;league_keys=390.l.963114/standings"
# r = oauth.session.get(url)
# print(r.status_code)
# 
# # Convert to string and remove namespace. Parse the string and return root element of Tree 
# xmlstring = r.text
# xmlstring = re.sub(' xmlns="[^"]+"', '', xmlstring, count=1)
# root = ET.fromstring(xmlstring)
# 
# # Initiate mylist
# mylist = []
# 
# # For loop statement that will loop through appropriate elemental tags and return associated text content. Save that text content into dictionary and add dictionary to mylist.
# team_keys = []
# allteams = root.findall('./leagues/league/standings/teams/team')
# for team in allteams:
#     team_key = team.find('team_key')  # same level
#     team_key = team_key.text
#     team_keys.append(team_key)
# 
#     name = team.find('name')
#     name = name.text
#     number_of_moves = team.find('number_of_moves')
#     number_of_moves = number_of_moves.text
#     number_of_trades = team.find('number_of_trades')
#     number_of_trades = number_of_trades.text
#     for nickname in team.iter('nickname'):  # all at all levels
#         nickname = nickname.text
#     for season in team.iter('season'):
#         season = season.text
#     for points_for in team.iter('points_for'):
#         points_for = points_for.text
#     for points_against in team.iter('points_against'):
#         points_against = points_against.text
#     for rank in team.iter('rank'):
#         rank = rank.text
#     for wins in team.iter('wins'):
#         wins = wins.text
#     for losses in team.iter('losses'):
#         losses = losses.text
#     for ties in team.iter('ties'):
#         ties = ties.text
#     for playoff_seed in team.iter('playoff_seed'):
#         playoff_seed = playoff_seed.text
#     thisdict = dict(season=season, name=nickname, team_name=name, team_key=team_key, rank=rank,
#                     wins=wins, losses=losses, ties=ties, points_for=points_for, points_against=points_against,
#                     number_of_moves=number_of_moves, number_of_trades=number_of_trades)
#     mylist.append(thisdict)
# 
# # get team data
# team_matchups = {}
# allteamsurl = "https://fantasysports.yahooapis.com/fantasy/v2/teams;team_keys="
# for tkey in team_keys:
#     allteamsurl += tkey + ','
# allteamsurl = allteamsurl[:-1] + "/matchups;weeks=1,2,3,4,5,6,7,8,9,10,11,12,13"
# r2 = oauth.session.get(allteamsurl)
# print(r2.status_code)

# Convert to string and remove namespace. Parse the string and return root element of Tree 
# xmlstringteams = r2.text
# xmlstringteams = re.sub(' xmlns="[^"]+"', '', xmlstringteams, count=1)
# rootteams = ET.fromstring(xmlstringteams)

## text_file = open("matchups.xml", "w")
## text_file.write(xmlstringteams)


class WinMargin:
    def __init__(self, start):
        self.margin = start
        self.week = -1
        self.team = "none"
        self.opponent = "none"


class Player:
    def __init__(self):
        self.full_name = ""
        self.weeklyscores = defaultdict(lambda: 0)
        self.weeklyposition = defaultdict(lambda: "FA")
        self.totalscore = 0
        self.weekTeamOwned = defaultdict(lambda: None)  # who had this player on roster for what weeks
        self.lastTeamOwnedID = ""  # TODO remove
        self.lastTeamOwnedName = ""  # TODO remove
        self.eligible_positions = []


class Team:
    def __init__(self):
        self.name = ""
        self.weeklyScores = {}
        self.opponentWeeklyScores = {}
        self.opponentName = {}
        self.opponentKey = {}
        self.weeklyProjScores = {}
        self.weeklyPlayers = defaultdict(lambda: [])  # list of player IDs with week as key 
        self.biggestWin = WinMargin(-1)
        self.smallestWin = WinMargin(999)


AllPlayers = defaultdict(lambda: Player())
AllTeams = defaultdict(lambda: Team())

allteamsurl = "https://fantasysports.yahooapis.com/fantasy/v2/teams;team_keys=390.l.963114.t.3,390.l.963114.t.8,390.l.963114.t.13,390.l.963114.t.9,390.l.963114.t.7,390.l.963114.t.4,390.l.963114.t.11,390.l.963114.t.6,390.l.963114.t.14,390.l.963114.t.5,390.l.963114.t.2,390.l.963114.t.10,390.l.963114.t.12,390.l.963114.t.1/matchups;weeks=1,2,3,4,5,6,7,8,9,10,11,12,13"
text_file = open("matchups.xml", "r")

rootteams = ET.fromstring(text_file.read())

allmatchups = rootteams.findall('./teams/team/matchups/matchup')
for matchup in allmatchups:
    week = matchup.find("week").text
    teams = matchup.findall('teams/team/name')
    team1name = teams[0].text
    team2name = teams[1].text
    teamkeys = matchup.findall('teams/team/team_key')
    team1key = teamkeys[0].text
    team2key = teamkeys[1].text
    team1score = float(matchup.findall('teams/team/team_points/total')[0].text)
    team2score = float(matchup.findall('teams/team/team_points/total')[1].text)
    team1projected = float(matchup.findall('teams/team/team_projected_points/total')[0].text)
    team2projected = float(matchup.findall('teams/team/team_projected_points/total')[1].text)

    AllTeams[team1key].name = team1name
    AllTeams[team1key].weeklyScores[week] = team1score
    AllTeams[team1key].weeklyProjScores[week] = team1projected
    AllTeams[team1key].opponentWeeklyScores[week] = team2score
    AllTeams[team1key].opponentName[week] = team2name
    AllTeams[team1key].opponentKey[week] = team2key

    AllTeams[team2key].name = team2name
    AllTeams[team2key].weeklyScores[week] = team2score
    AllTeams[team2key].weeklyProjScores[week] = team2projected
    AllTeams[team2key].opponentWeeklyScores[week] = team1score
    AllTeams[team2key].opponentName[week] = team1name
    AllTeams[team2key].opponentKey[week] = team1key

################ determine biggest and smallest wins ############################
for team in AllTeams.values():
    matchupScore = zip(team.weeklyScores.keys(), team.weeklyScores.values(), team.opponentWeeklyScores.values(),
                       team.opponentName.values())
    for week, mine, yours, yourname in matchupScore:
        scoreDiff = mine - yours
        if scoreDiff > 0:
            if scoreDiff > team.biggestWin.margin:
                team.biggestWin.margin = scoreDiff
                team.biggestWin.week = week
                team.biggestWin.opponent = yourname
                team.biggestWin.team = team.name
            if scoreDiff < team.smallestWin.margin:
                team.smallestWin.margin = scoreDiff
                team.smallestWin.week = week
                team.smallestWin.opponent = yourname
                team.smallestWin.team = team.name

##############download all rosters##########################
### https://fantasysports.yahooapis.com/fantasy/v2/team//roster;week=10
# rosterurl = "https://fantasysports.yahooapis.com/fantasy/v2/teams;team_keys=390.l.963114.t.3,390.l.963114.t.8,390.l.963114.t.13,390.l.963114.t.9,390.l.963114.t.7,390.l.963114.t.4,390.l.963114.t.11,390.l.963114.t.6,390.l.963114.t.14,390.l.963114.t.5,390.l.963114.t.2,390.l.963114.t.10,390.l.963114.t.12,390.l.963114.t.1/roster;week="
# for i in range(1, 2):
#     thisweekrosterurl = rosterurl + str(i)
#     # url = "https://fantasysports.yahooapis.com/fantasy/v2/leagues;league_keys=390.l.963114/standings"
#     r = oauth.session.get(thisweekrosterurl)
#     print("week" + str(i) + "  " + str(r.status_code))
#     xmlstring = r.text
#     xmlstring = re.sub(' xmlns="[^"]+"', '', xmlstring, count=1)
#     text_file = open("rosterweek" + str(i) + ".xml", "w")
#     text_file.write(xmlstring)
# 
# # Convert to string and remove namespace. Parse the string and return root element of Tree 

####### Iterate rosters #####

for i in range(1, 14):
    rosterfile = open("rosterweek{}.xml".format(i), "r")
    rosterweek = ET.fromstring(rosterfile.read())
    for team in rosterweek.findall('./teams/team'):
        teamkey = team.find("team_key").text
        teamname = team.find("name").text
        for player in team.findall('./roster/players/player'):
            playerid = player.find("player_id").text
            fullname = player.find("./name/full").text
            positions = player.findall('./eligible_positions/position')
            thisweekpos = player.find("./selected_position/position").text

            AllPlayers[playerid].eligible_positions = [x.text for x in positions]
            AllPlayers[playerid].full_name = fullname
            AllPlayers[playerid].weeklyposition[i] = thisweekpos
            AllPlayers[playerid].lastTeamOwnedID = teamkey
            AllPlayers[playerid].lastTeamOwnedName = teamname
            AllPlayers[playerid].weekTeamOwned[i] = teamname
            AllTeams[teamkey].weeklyPlayers[i].append(playerid)

            # print(len(AllPlayers.keys())) #total activated players
    for filename in os.listdir("."):  # player stats
        if "playerstatweek" + str(i) + "." in filename:
            playerstatweekfile = open(filename, "r")
            weekroot = ET.fromstring(playerstatweekfile.read())
            for player in weekroot.findall('./league/players/player'):
                playerid = player.find("player_id").text
                points = float(player.find('./player_points/total').text)
                AllPlayers[playerid].totalscore += points
                AllPlayers[playerid].weeklyscores[i] = points

########### DL all player data of players who played this year ############################
# max data is 2000  or 32779           
# maxURLsize = 32779
# 
# 
# #### get player data
# ## fill all points all players
# def SaveWeekPlayerData(geturl, weeknum, playerNum):
#     fullURL = geturl + weeknum
#     reqsize = len(fullURL)
#     print(reqsize)
#     r = oauth.session.get(fullURL)
#     xmlstring = r.text
#     xmlstring = re.sub(' xmlns="[^"]+"', '', xmlstring, count=1)
#     weekdatafile = open("playerstatweek" + weeknum + "." + playerNum + ".xml", "w")
#     weekdatafile.write(xmlstring)
# 
# 
# playersurlstart = "https://fantasysports.yahooapis.com/fantasy/v2/league/390.l.963114/players;player_keys="
# playersurlend = "/stats;type=week;week="
# gamestr = "390.p."
# playersurl = playersurlstart
# playercnt = len(AllPlayers.keys())
# maxplayerQuery = 25  # yahoo max query size gross ugh
# for weeknum in range(1, 14):
#     playersurl = playersurlstart
#     for i, playerid in enumerate(AllPlayers.keys()):
#         if i == playercnt - 1:  # is last key
#             playersurl += gamestr + playerid + ","
#             SaveWeekPlayerData(playersurl[:-1] + playersurlend, str(weeknum), str(i))
#         elif i != 0 and i % maxplayerQuery == 0:
#             SaveWeekPlayerData(playersurl[:-1] + playersurlend, str(weeknum), str(i))
#             playersurl = playersurlstart
#             playersurl += gamestr + playerid + ","
#         elif len(playersurl) + len(playersurlend) + len(playerid) + len(gamestr) + 10 < maxURLsize:  # more size left
#             playersurl += gamestr + playerid + ","
#         else:  # is max size URL 
#             SaveWeekPlayerData(playersurl[:-1] + playersurlend, str(weeknum), str(i))
#             playersurl = playersurlstart
#             playersurl += gamestr + playerid + ","


print()
print("$15 'El Juggernauto', Top Player:")
highestPlayer = Player()
for playerid, player in AllPlayers.items():
    if player.totalscore > highestPlayer.totalscore:
        highestPlayer = player
print("{}, {}, {:.2f} pts".format(highestPlayer.full_name, highestPlayer.lastTeamOwnedName, highestPlayer.totalscore))

print()
print("$15 'A Peyton Manning Superbowl', Biggest win:")
biggestMargin = WinMargin(0)
for team in AllTeams.values():
    if team.biggestWin.margin > biggestMargin.margin:
        biggestMargin = team.biggestWin
print("{} over {}, {:.2f} pts, week {}".format(biggestMargin.team, biggestMargin.opponent, biggestMargin.margin,
                                               biggestMargin.week))

print()
print("$15 'Finger prodder', Smallest win:")
smallestMargin = WinMargin(999)
for team in AllTeams.values():
    if team.smallestWin.margin < smallestMargin.margin:
        smallestMargin = team.smallestWin
print("{} over {}, {:.2f} pts, week {}".format(smallestMargin.team, smallestMargin.opponent, smallestMargin.margin,
                                               smallestMargin.week))

print()
print("$15 'The Balloon Experiment', Highest week team score:")
highestWeekScore = 0
highestWeekScoreWeek = 0
highestWeekScoreTeam = ""
for team in AllTeams.values():
    for week, score in team.weeklyScores.items():
        if score > highestWeekScore:
            highestWeekScoreWeek = week
            highestWeekScore = score
            highestWeekScoreTeam = team.name
print("{0}, {1:.2f} pts, week {2} ".format(highestWeekScoreTeam, highestWeekScore, highestWeekScoreWeek))

print()
print("$15 'Jesus Chris', Highest week single player score:")
highestWeekPlayer = Player()
highWeekPlayerScore = 0
highWeekPlayerWeek = 0
for player in AllPlayers.values():
    for week, weekscore in player.weeklyscores.items():
        if weekscore > highWeekPlayerScore:
            highWeekPlayerScore = weekscore
            highWeekPlayerWeek = week
            highestWeekPlayer = player
print("{}, {}, {:.2f} pts, week {} ".format(highestWeekPlayer.full_name, highestWeekPlayer.lastTeamOwnedName,
                                            highWeekPlayerScore, highestWeekScoreWeek))

print()
print("$5 'The WTF', Most negative weekly single player score:")
lowestWeekPlayer = Player()
lowestWeekPlayerScore = 0
lowestWeekPlayerWeek = 0
lowestWeekPlayerTeam = ""
for player in AllPlayers.values():
    for week, weekscore in player.weeklyscores.items():
        if weekscore < lowestWeekPlayerScore and player.weeklyposition[
            week] != "BN" and "DEF" not in player.eligible_positions and player.weekTeamOwned[week] is not None:
            lowestWeekPlayerScore = weekscore
            lowestWeekPlayerWeek = week
            lowestWeekPlayer = player
            lowestWeekPlayerTeam = player.weekTeamOwned[week]
print("{}, {}, {:.2f} pts, week {} ".format(lowestWeekPlayer.full_name, lowestWeekPlayerTeam,
                                            lowestWeekPlayerScore, lowestWeekPlayerWeek))

print()
print("$15 'Commander-in-chief', Most Regular Season Point For:")
highestSeasonTeamFor = Team()
highestSeasonTeamForPoints = 0
for team in AllTeams.values():
    thisTeamScore = sum(team.weeklyScores.values())
    if thisTeamScore > highestSeasonTeamForPoints:
        highestSeasonTeamForPoints = thisTeamScore
        highestSeasonTeamFor = team
print("{}, {:.2f} pts".format(highestSeasonTeamFor.name, highestSeasonTeamForPoints))

print()
print("$15 'The Jamarcus Russell', Most Regular Season Point Against:")
highestSeasonTeamAgainst = Team()
highestSeasonTeamAgainstPoints = 0
for team in AllTeams.values():
    thisTeamScore = sum(team.opponentWeeklyScores.values())
    if thisTeamScore > highestSeasonTeamAgainstPoints:
        highestSeasonTeamAgainstPoints = thisTeamScore
        highestSeasonTeamAgainst = team
print("{}, {:.2f} pts".format(highestSeasonTeamAgainst.name, highestSeasonTeamAgainstPoints))