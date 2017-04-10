import discord 
from discord.ext import commands
from cogs.utils.dataIO import dataIO
import json
import os

try:
    import challonge
except:
    print("No challonge module detected. Please install pychal instead of pychallonge. pychallonge is outdated.")
    raise

leadRole = "Officer"
botRole = "ShallusBot Dev"

#This class will allow users in a server to track challonge
#tournaments. Looking up opponents and updating scores will
#also be supported.
class Bracket:
    """Begin/Stop tracking a tournament, update scores, get next opponent, get players of a match."""

    def __init__(self, bot):
        self.bot = bot
        self.username = None
        self.api = None
    
    @commands.command(pass_context=True)
    async def track(self, ctx, url):
        """Begin tracking a Challonge tournament.\nDon't include the challonge.com part.\nExample: If the tournament you want to track has the url challonge.com/trackme, then just type trackme.\nOnly officers can use this command."""
        serverId = ctx.message.server.id
        path = "data/bracket/" + serverId + "/tracklist.json"
        author = ctx.message.author

        rolelist = author.roles
        isOfficer = False

        global leadRole
        global botRole

        for roles in rolelist:
            if roles.name == leadRole or roles.name == botRole:
                isOfficer = True

        if not isOfficer:
            await self.bot.say("You are not an officer. Only officers can use this command.")
            return
        
        else:
        
            #make sure the server has a folder for tracklist to be inside.
            if not os.path.exists("data/bracket/" + serverId):
                print("Creating a new directory for server " + ctx.message.server.name)
                os.makedirs("data/bracket/" + serverId)
        
            #check to see if a tournament is being tracked or not.
            if not dataIO.is_valid_json(path):
                print("Creating new trackfile for server with id " + serverId)
                dataIO.save_json(path, {})
            else:
                await self.bot.say("A tournament is already being tracked. Please stop tracking your current tournament to track a new tournament.")
                return

            #establish connection to challonge and get tournament data
            userdata = dataIO.load_json("data/bracket/login.json")
            challonge.set_credentials(userdata["username"], userdata["api_key"])
            tourn = challonge.tournaments.show(url)
            await self.bot.say("Found a tournament with this url called " + tourn["name"] + ". Begin tracking this? (yes/no)")

            answer = await self.bot.wait_for_message(timeout=15, author=author)
            
            if answer == None or not answer.content.lower().strip() == "yes": 
                os.remove(path)
                await self.bot.say("No action was taken. I did not track " + tourn["name"] + ".")
                return
        
            #JSON object of matches
            await self.bot.say("Creating tracking file...")
            jsonMatch = []
            item = {}
            matches = challonge.matches.index(tourn["id"])
            for entry in matches:
                item[entry["identifier"]] = entry["id"]
            jsonMatch.append(item)

            #JSON object of players
            jsonPlayer = []
            item = {}
            players = challonge.participants.index(tourn["id"])
            for player in players:
                item[player["name"]] = player["id"]
            jsonPlayer.append(item)
        
            #the JSON data will contain id, url, name, and JSON objects of the matches and players.
            info = info = {"id": tourn["id"], "url": url, "name": tourn["name"], "matches": jsonMatch, "players": jsonPlayer}
            dataIO.save_json(path, info)
            await self.bot.say("Tracking tournament " + tourn["name"] + ".")

    @commands.command(pass_context=True)
    async def stoptrack(self, ctx):
        """Stop tracking a tournament. Only officers can use this command."""

        path = "data/bracket/" + ctx.message.server.id + "/tracklist.json"
        author = ctx.message.author

        rolelist = author.roles
        isOfficer = False
        global leadRole
        global botRole

        for roles in rolelist:
            if roles.name == leadRole or roles.name == botRole:
                isOfficer = True

        if not isOfficer:
            await self.bot.say("You are not an officer. Only officers can use this command.")
            return
        else:

            #check to see if a tournament is being tracked or not. Remove tracklist file to stop tracking.
            if dataIO.is_valid_json(path):
                userdata = dataIO.load_json(path)
                name = userdata["name"]
                await self.bot.say("Currently tracking " + name + ". Are you sure you want to stop tracking this tournament? (yes/no)")
                answer = await self.bot.wait_for_message(timeout=15, author=author)
            
                if answer == None or not answer.content.lower().strip() == "yes": 
                    await self.bot.say("No action was taken. I did not stop tracking " + name + ".")
                else:
                    os.remove(path)
                    await self.bot.say("Not longer tracking " + name + ".")
        
            #No track file found.
            else:
                await self.bot.say("Currently not tracking a tournament.")

    @commands.command(pass_context=True)
    async def opponent(self, ctx, player):
        """Output the opponent of the player entered.\nCASE SENSITIVE!\nExample: If you want to find your next opponenet, use your tag."""
        
        path = "data/bracket/" + ctx.message.server.id + "/tracklist.json"

        #check to see if a tournament is being tracked or not. Search through matches if a tournament is being tracked.
        if dataIO.is_valid_json(path):
            userdata = dataIO.load_json(path)
            
            #Make sure player exists by checking the players list in the JSON file.
            if not player in userdata["players"][0]:
                await self.bot.say("This player name is not in the tournament. Please double check spelling and capitalization.")
            else:
                await self.bot.say("Searching...")
                
                #obtain the login credentials and login.
                login = dataIO.load_json("data/bracket/login.json")
                challonge.set_credentials(login["username"], login["api_key"])

                playerId = userdata["players"][0][player]
                matches = challonge.matches.index(userdata["id"])

                for match in matches:
                    
                    #Given player is either not in this match, or the winner of the match has already been decided.
                    #Ignore these cases.
                    if (not match["winner_id"] == None) or (not playerId == match["player1_id"] and not playerId == match["player2_id"]):
                            continue
                    else:
                        
                        #Player is player 1. Return information about player 2 in this scenario.
                        if playerId == match["player1_id"]:
                            
                            #There is a player 2. Just return the name of player 2.
                            if not match["player2_id"] == None:
                                await self.bot.say(player + "'s opponent will be " + challonge.participants.show(userdata["id"], match["player2_id"])["name"])
                                return
                            else:
                                
                                #No player 2. This means that the match to determine player 2 hasn't been completed. Print conditions of previous match to determine player 2.
                                if match["player2_is_prereq_match_loser"] == False:
                                    await self.bot.say(player + "'s opponent will be the winner of Match " + challonge.matches.show(userdata["id"], match["player2_prereq_match_id"])["identifier"])
                                    return
                                else:
                                    await self.bot.say(player + "'s opponent will be the loser of Match " + challonge.matches.show(userdata["id"], match["player2_prereq_match_id"])["identifier"])
                                    return
                        
                        #Player is player 2. Return information about player 1 in this scenario.
                        else:
                            
                            #There is a player 1. Just return name of player 1.
                            if not match["player1_id"] == None:
                                await self.bot.say(player + "'s opponent will be " + challonge.participants.show(userdata["id"], match["player1_id"])["name"])
                                return
                            else:
                                
                                #No player 1. This means that the match to determine player 2 hasn't been completed. Print conditions of previous match to determine player 2.
                                if match["player1_is_prereq_match_loser"] == False:
                                    await self.bot.say(player + "'s opponent will be the winner of Match " + challonge.matches.show(userdata["id"], match["player1_prereq_match_id"])["identifier"])
                                    return
                                else:
                                    await self.bot.say(player + "'s opponent will be the loser of Match " + challonge.matches.show(userdata["id"], match["player1_prereq_match_id"])["identifier"])
                                    return
                
                #if we exit the loop, then this player has already been eliminated. 
                await self.bot.say("This player has already been eliminated")
                return                       

        #No track file found.
        else:
            await self.bot.say("Currently not tracking a tournament.")

    @commands.command(pass_context=True)
    async def reportscore(self, ctx, player1, player2, score1, score2):
        """Report the scores of an unsettled match.\nExample: If it was john vs jim, and jim won 3 to 2, enter john, jim, 2, 3.\nUse !updatescore if you want to change the scores of a match."""

        if player1 == player2:
            await self.bot.say("You entered the same name twice. Please enter different names.")
            return
      
        path = "data/bracket/" + ctx.message.server.id + "/tracklist.json"
        author = ctx.message.author

        #check to see if a tournament is being tracked or not. Change match score if a tournament is being tracked.
        if dataIO.is_valid_json(path):

            userdata = dataIO.load_json(path)


            #make sure player exists by checking the players list in the JSON file
            if not player1 in userdata["players"][0] and not player2 in userdata["players"][0]:
                await self.bot.say("At least one of the 2 players is not in the tournament. Please double check spelling and capitalization.")

            else:

                #attempt to convert the scores entered to integers.
                try:
                    set1 = int(score1)
                    set2 = int(score2)

                    if set1 == set2:
                        await self.bot.say("You entered the same score. Only update the score when the match has been concluded.")
                        return

                except ValueError:
                    await self.bot.say("Please enter integers for the scores")
                    return

                #obtain the login credentials and login.
                login = dataIO.load_json("data/bracket/login.json")
                challonge.set_credentials(login["username"], login["api_key"])

                matches = challonge.matches.index(userdata["id"])

                #get ids for the players
                player1id = userdata["players"][0][player1]
                player2id = userdata["players"][0][player2]

                #search through all of the matches until we find the match with the 2 players, and update the score.
                for match in matches:

                    #The 2 players are not playing each other in this match. Skip to next match.
                    if not (match["player1_id"] == player1id and match["player2_id"] == player2id) and not (match["player1_id"] == player2id and match["player2_id"] == player1id) or not match["winner_id"] == None:
                        continue
                    else:
                        
                        #rearrange names/scores with temp vars to help with updating score.
                        actualPlayer1 = ""
                        actualPlayer2 = ""
                        actual1id = ""
                        actual2id = ""
                        actualScore1 = 0
                        actualScore2 = 0

                        #match player1 is the same as player1
                        if match["player1_id"] == player1id:
                            actualPlayer1 = player1
                            actualPlayer2 = player2
                            actual1id = player1id
                            actual2id = player2id
                            actualScore1 = set1
                            actualScore2 = set2

                        #match player1 is the same as player2
                        else:
                            actualPlayer1 = player2
                            actualPlayer2 = player1
                            actual1id = player2id
                            actual2id = player1id
                            actualScore1 = set2
                            actualScore2 = set1

                        #Also need to determine winner and their id
                        winner = ""
                        winnerid = ""
                        loserid = ""

                        #Score1 > Score2 means player 1 is the winner. Else player 2 is.
                        if actualScore1 > actualScore2:
                            winner = actualPlayer1
                            winnerid = actual1id
                            loserid = actual2id
                        else:
                            winner = actualPlayer2
                            winnerid = actual2id
                            loserid = actual1id

                        await self.bot.say(actualPlayer1 + " vs " + actualPlayer2 + "\nThe score was " + str(actualScore1) + "-" + str(actualScore2) + ".\nThe winner is " + winner + ".\nMake sure this is correct.\nProceed with update? (yes/no)")
                        
                        answer = await self.bot.wait_for_message(timeout=15, author=author)
                        if answer == None or not answer.content.lower().strip() == "yes": 
                            await self.bot.say("Score was not updated.")
                        else:
                            score_csv = str(actualScore1) + "-" + str(actualScore2)
                            print(match)
                            newmatch = {"match": match}

                            #make sure that this is possible. Error if trying to update a tourney that isn't yours.
                            try:
                                challonge.matches.update(userdata["id"], match["id"], scores_csv = score_csv, winner_id = winnerid, player1_votes = actualScore1, player2_votes = actualScore2)
                                await self.bot.say("Score was updated.")

                            except urllib2.HTTPError as err:
                                await self.bot.say("Oops. Something went wrong. Make sure " + login["username"] + " created the tournament so I can edit the score. Otherwise, try again later.")
                                raise
                        return



                #If we exit the loop, this means that the 2 players are not playing in the same match.
                await self.bot.say("Found no match where these 2 players are fighting. Please double check the player tags. If you want to correct a match score, contact an officer to use !updatescore.")
                return


        #No track file found.
        else:
            await self.bot.say("Currently not tracking a tournament.")

    @commands.command(pass_context=True)
    async def match(self, ctx, letter):
        """List the players of a given match.\nUse only capital letters.\nChallonge gave us the data in letters instead of numbers.\nTo figure out what letter a match is on the website, count all of the winner matches first (down then right). Then count the loser matches in order."""
        
        path = "data/bracket/" + ctx.message.server.id + "/tracklist.json"

        #check to see if a tournament is being tracked or not. Search through matches if a tournament is being tracked.
        if dataIO.is_valid_json(path):
            userdata = dataIO.load_json(path)
            #Make sure match exists by checking the matches list in the JSON file.
            if not letter in userdata["matches"][0]:
                login = dataIO.load_json("data/bracket/login.json")
                challonge.set_credentials(login["username"], login["api_key"])

                matches = challonge.matches.index(userdata["id"])

                for match in matches:
                    await self.bot.say(match["identifier"])
                
                await self.bot.say("There is no match corresponding to this letter.")
            else:

                await self.bot.say("Searching...")

                #obtain the login credentials and login.
                login = dataIO.load_json("data/bracket/login.json")
                challonge.set_credentials(login["username"], login["api_key"])

                match = challonge.matches.show(userdata["id"], userdata["matches"][0][letter])

                #Both players are decided in the match.
                if not match["player1_id"] == None and not match["player2_id"] == None:
                    await self.bot.say(challonge.participants.show(userdata["id"], match["player1_id"])["name"] + " will be facing " + challonge.participants.show(userdata["id"], match["player2_id"])["name"] + ".")

                    #If winner has been determined, then also say who won the match.
                    if not match["winner_id"] == None:
                        await self.bot.say("This match has concluded. The winner was " + challonge.participants.show(userdata["id"], match["winner_id"])["name"])

                else:
                    player1 = ""
                    player2 = ""
                    
                    #Player 1 hasn't been determined yet.
                    if match["player1_id"] == None:
                        if match["player1_is_prereq_match_loser"] == False:
                            player1 = "The winner of Match " + challonge.matches.show(userdata["id"], match["player1_prereq_match_id"])["identifier"]
                        else:
                            player1 = "The loser of Match " + challonge.matches.show(userdata["id"], match["player1_prereq_match_id"])["identifier"]

                    #Player 1 is determined.
                    else:
                        player1 = challonge.participants.show(userdata["id"], match["player1_id"])["name"]

                    #Player 2 hasn't been determined yet.
                    if match["player2_id"] == None:
                        if match["player2_is_prereq_match_loser"] == False:
                            player2 = "the winner of Match " + challonge.matches.show(userdata["id"], match["player2_prereq_match_id"])["identifier"]
                        else:
                            player2 = "the loser of Match " + challonge.matches.show(userdata["id"], match["player2_prereq_match_id"])["identifier"]

                    #Player 2 is determined.
                    else:
                        player2 = challonge.participants.show(userdata["id"], match["player2_id"])["name"]

                    await self.bot.say(player1 + " will be facing " + player2 + ".")


        #No track file found.
        else:
            await self.bot.say("Currently not tracking a tournament.")

    @commands.command(pass_context=True)
    async def updatescore(self, ctx, matchletter, score1, score2):
        """Change the scores of a match, even if scores have already been entered for the match.\nOnly officers can use this command."""
      
        path = "data/bracket/" + ctx.message.server.id + "/tracklist.json"
        author = ctx.message.author

        rolelist = author.roles
        isOfficer = False
        global leadRole
        global botRole

        for roles in rolelist:
            if roles.name == leadRole or roles.name == botRole:
                isOfficer = True

        if not isOfficer:
            await self.bot.say("You are not an officer. Only officers can use this command.")
            return

        else:

            #check to see if a tournament is being tracked or not. Change match score if a tournament is being tracked.
            if dataIO.is_valid_json(path):
                userdata = dataIO.load_json(path)

                #Make sure match exists by checking the matches list in the JSON file.
                if not matchletter in userdata["matches"][0]:
                    await self.bot.say("There is no match corresponding to this letter.")
            
                else:

                    #attempt to convert the scores entered to integers.
                    try:
                        set1 = int(score1)
                        set2 = int(score2)

                        if set1 == set2:
                            await self.bot.say("You entered the same score. Only update the score when the match has been concluded.")
                            return

                    except ValueError:
                        await self.bot.say("Please enter integers for the scores")
                        return

                    #obtain the login credentials and login.
                    login = dataIO.load_json("data/bracket/login.json")
                    challonge.set_credentials(login["username"], login["api_key"])
                
                    match = challonge.matches.show(userdata["id"], userdata["matches"][0][matchletter])
                    if set1 < set2:
                        winnerid = match["player2_id"]
                        winner = challonge.participants.show(userdata["id"], match["player2_id"])["name"]
                    else:
                        winnerid = match["player1_id"]
                        winner = challonge.participants.show(userdata["id"], match["player1_id"])["name"]

                    await self.bot.say(challonge.participants.show(userdata["id"], match["player1_id"])["name"] + " vs " + challonge.participants.show(userdata["id"], match["player2_id"])["name"] + "\nThe new score is " + str(score1) + "-" + str(score2) + ".\nThe winner afterwards is " + winner + ".\nPLEASE MAKE SURE THAT THIS IS ACCURATE.\nProceed with update? (yes/no)")

                    answer = await self.bot.wait_for_message(timeout=15, author=author)
                    if answer == None or not answer.content.lower().strip() == "yes": 
                        await self.bot.say("Score was not updated.")
                    else:
                        score_csv = score1 + "-" + score2
                        newmatch = {"match": match}

                        #make sure that this is possible. Error if trying to update a tourney that isn't yours.
                        try:
                            await self.bot.say("Updating score...")
                            challonge.matches.update(userdata["id"], match["id"], scores_csv = score_csv, winner_id = winnerid, player1_votes = score1, player2_votes = score2)
                            await self.bot.say("Score was updated.")

                        except:
                            await self.bot.say("Oops. Something went wrong. Make sure " + login["username"] + " created the tournament so I can edit the score. Otherwise, try again later.")
                            raise
                            
            #No track file found.
            else:
                await self.bot.say("Currently not tracking a tournament.")

    @commands.command(pass_context=True)
    async def bracketurl(self, ctx):
        """Get the url link for the current tournament being tracked."""

        path = "data/bracket/" + ctx.message.server.id + "/tracklist.json"

        #check to see if a tournament is being tracked or not. Search through matches if a tournament is being tracked.
        if dataIO.is_valid_json(path):
            userdata = dataIO.load_json(path)

            await self.bot.say("The url of the current tournament being tracked is www.challonge.com/" + userdata["url"])

        else:
            await self.bot.say("Currently not tracking a tournament.")

#make sure all of the correct files are created already.
def check_files():
    f = "data/bracket/login.json"
    if not dataIO.is_valid_json(f):
        print("Creating a new login file.")
        login = {"username": "dummy", "api_key": "dS247Td0LWZd0tK2MTaXkud1x7dWLq3SXxbL4ieX"}
        dataIO.save_json(f, login)

#make sure all of the required folders are created already.
def check_folders():
    if not os.path.exists("data/bracket"):
        print("Creating data/bracket folder...")
        os.makedirs("data/bracket")

def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(Bracket(bot))
