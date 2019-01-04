"""Script scrapes through multiples urls to compile a list of players
   from the english premier league along with their fantasy league statistics
   in order to create an excel sheet containing the statistics of the league's
   top performers in each position
   """

import json
import urllib.request
import xlsxwriter

'''ids associated with positions'''
goalKeeper = 1
defender = 2
midfielder = 3
forward = 4

'''urls for scraping'''
playerListURL = "https://fantasy.premierleague.com/drf/elements/"   #contains player information
teamListURL = "https://fantasy.premierleague.com/drf/teams/"        #contains team information
fixtureListURL = "https://fantasy.premierleague.com/drf/fixtures/"  #contains fixture statistics
gameWeekListURL = "https://fantasy.premierleague.com/drf/events/"   #contains game week statistics


'''Takes in url and returns a list of dicts after scraping url'''
def scrape(url):
    with urllib.request.urlopen(url) as url:
        raw_data = url.read()
    return json.loads(raw_data)

'''Takes in a player position and returns a list of
   players that play that position'''
def getPlayerList(playerPosition):

    playerList = []

    #scrape url for all player elements
    raw_playerList = scrape(playerListURL)

    #filter players for required position and then append to final player list
    for player in raw_playerList:
        if player["element_type"] == playerPosition:
            playerList.append(player)

    return playerList

'''Takes in a list of players and returns a list of 
   objects containing player name, team, next opponent,
   and a list of points they accumulated each game week'''
def getPlayerStatisics(playerList):

    playerPerfomanceList = []

    #scrape url for all game week elements
    gameWeekList = scrape(gameWeekListURL)
    currentGameWeek = None

    #Find number of last game week completed
    for gameWeek in gameWeekList:
        if gameWeek['is_current'] == True:
            currentGameWeek = gameWeek['id']


    #gather pertinent information for each player in list and put into dict
    for player in playerList:

        playerPerfomance = {}
        pointDistribution = []

        playerPerfomance['name'] = player['first_name'] + " " + player['second_name']

        #scarpe url for all team elements
        teamList = scrape(teamListURL)
        playerPerfomance['team'] = teamList[player['team']-1]['name']
        playerPerfomance['next fixture'] = teamList[teamList[player['team']-1]['next_event_fixture'][0]['opponent']-1]['name']

        #scrape url for all fixture elements
        fixtureList = scrape(fixtureListURL)

        i = 0
        #keep track of game week
        gameWeekCounter = 1
        while i < len(fixtureList):

            fixture = fixtureList[i]
            #keep track if player played in certain game week
            played = False
            homeOrAway = None

            #check if players team was home or away in a fixture
            if fixture['event'] <= currentGameWeek:
                if player['team'] == fixture['team_h']:
                    homeOrAway = 'h'
                elif player['team'] == fixture['team_a']:
                    homeOrAway = 'a'

                if homeOrAway:
                    #even though team is in fixture maybe player did not play that day
                    for playerPoints in fixture['stats'][9]['bps'][homeOrAway]:
                        if playerPoints['element'] == player['id']:
                            played = True
                            pointDistribution.append(playerPoints['value'])
                            break
                    if not played:
                        pointDistribution.append(0)

                    #since player only plays one fixture per game week skip other fixtures
                    # and move onto next game week
                    gameWeekCounter += 1
                    i = gameWeekCounter * 10 - 10
                else:
                    # if the players team was neither home or away
                    # that means you move on to the next fixture in the game week
                    i += 1

            else:
                #once current game week is reached break and ignore rest of game weeks
                break

        #save points list to player dict and add to list of player dicts
        playerPerfomance['pointDistribution'] = pointDistribution
        playerPerfomanceList.append(playerPerfomance)

    return playerPerfomanceList

'''Takes in number of top performers, number of recent fixtures to look at, 
   and a list of players and returns a sorted list of the top n performers
   in the last n fixtures'''
def sortTopPerfomers(numPerformers, numFixtures, playerPerformanceList):
    return sorted(playerPerformanceList, key = lambda stats: sum(stats['pointDistribution'][-numFixtures:]), reverse=True)[:numPerformers]

'''Takes in list of top performers and number of fixtures to be displayed 
   and then produces .xlsx sheet with top performers info and points they 
   accumulated in each of the last n fixtures'''
def createExcelSheet(topPerformers, numFixtures):

    #open workbook or create if it doesn't exist
    workbook = xlsxwriter.Workbook('eplPlayerFantasyForm.xlsx')
    worksheet = workbook.add_worksheet()
    #make headers bold
    bold = workbook.add_format({'bold': 1})

    #Information to be displayed in worksheet
    headings = ['Player', 'Team', 'Next Fixture']

    i = len(topPerformers[0]['pointDistribution']) - numFixtures
    while i < len(topPerformers[0]['pointDistribution']):
        headings.append('GW'+str(i+1))
        i += 1

    #add headings to worksheet
    worksheet.write_row('A1', headings, bold)

    #fill in information for each player
    i = 0
    while i < len(topPerformers):
        worksheet.write_string(i+1,0,topPerformers[i]['name'])
        worksheet.write_string(i+1,1,topPerformers[i]['team'])
        worksheet.write_string(i+1,2,topPerformers[i]['next fixture'])
        j = 0
        while j < len(topPerformers[i]['pointDistribution'][-numFixtures:]):
            worksheet.write_string(i+1,j+3,str(topPerformers[i]['pointDistribution'][-numFixtures:][j]))
            j += 1
        i+=1

    workbook.close()

if __name__ == '__main__':

    print ("\n\tEPL Player Form")

    playerPosition = input("\nChoose position for form list\n\n\t"
                               "1 - Goalkeeper\n\t2 - Defender\n\t3 - Midfielder\n\t4 - Forward\n\n"
                               "Type corresponding number: ")

    if playerPosition == '1':
        print ("\nGoalkeeper selected")
    elif playerPosition == '2':
        print ("\nDefender selected")
    elif playerPosition == '3':
        print ("\nMidfielder selected")
    elif playerPosition == '4':
        print ("\nForward selected")
    else:
        print ("\nNot an option in the list")

    print("\nGathering list of players")
    playerList = getPlayerList(int(playerPosition))

    print ("\nGathering statistics for players")
    playerPerformanceList = getPlayerStatisics(playerList)

    numPerformers, numFixtures = input("\nGather top __ performers from the last __ game weeks\n"
                               "Type number of performers & game weeks (with a comma in between): ").split(",")

    print ("\nSorting out top " + numPerformers + " performers in the last " + numFixtures + " game weeks")
    topPerformers = sortTopPerfomers(int(numPerformers),int(numFixtures),playerPerformanceList)

    print ("\nGenerating Excel Sheet with top performers data")
    createExcelSheet(topPerformers, int(numFixtures))

    print ("\nDone. Exiting Program")