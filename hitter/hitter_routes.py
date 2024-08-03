from flask import render_template, request, jsonify
import pandas as pd
import random
import os
import csv
import statsapi
import asyncio
import unicodedata

from . import hitter_bp
streak = 0

# Get path for CSV file that contains player names, teams, and images
csv_path = os.path.join('extract', 'player_image.csv')

# Load player data from csv file into a DataFrame
df = pd.read_csv(csv_path, encoding='utf-8')

# All 30 team ids from MLB-StatsAPI
teams = [108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 158]

team_names = {}

# Load team_names using team ids
for team_id in teams:
    team_info = statsapi.lookup_team(team_id)
    name = team_info[0]['name']
    team_names[team_id] = name

# Generates and returns a random position player from any of the 30 mlb teams
def get_rand_player():
    teams = [108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 158]
    randTeam = random.choice(teams)
    roster = statsapi.roster(randTeam)
    lines = roster.split('\n')
    
    # Filter out pitchers ('P' is the position code for pitchers)
    filtered_lines = [line for line in lines if len(line.split()) > 1 and line.split()[1] != 'P']
    names = [' '.join(line.split()[2:]) for line in filtered_lines]
    filtered_names = '\n'.join(names)

    # Randomly select a player from the filtered list
    index = random.randrange(len(names))
    player = statsapi.lookup_player(names[index])

    # Return the first (and only) element of the player list
    return player[0]

# Returns the hits of a player given the player id
def get_player_stats(player_id):
    player_stats = statsapi.player_stat_data(player_id, group="[hitting]", type="career")
    try:
        player_hits = player_stats['stats'][0]['stats']['hits']
        return player_hits
    
    # Get a new player if they do not have a career hits value
    except IndexError:
        return "Get New Player"

# Returns the image url of a player given the player name and player team
def get_player_image(player_name, player_team):
    player = df[(df['name'] == player_name) & (df['team'] == player_team)]
    try:
        player_img = player['image_url'].values[0]
    
    # Return a generic silhouette image if the player is not found in the CSV file
    except IndexError:
        player_img = '/static/silhouette.jpg'
    return player_img

# Compares the hits of two players and returns the name of the player with the higher hits
def compare_hits(playerA, playerB):
    playerA_hits = get_player_stats(playerA[0]['id'])
    playerB_hits = get_player_stats(playerB[0]['id'])

    if playerA_hits > playerB_hits:
        return playerA[0]['fullName']
    elif playerB_hits > playerA_hits:
        return playerB[0]['fullName']
    else:
        return "Equal"


@hitter_bp.route('/')
def index():
    """
    Renders the main game page and resets the streak variable.
    """
    # Set the streak variable to 0 for every new session
    global streak
    streak = 0
    return render_template('hitter.html')

@hitter_bp.route('/start_game', methods=['GET'])
def start_game():
    """
    Starts a new game by selecting two random players, ensuring they are different.
    Returns the names and hits of both players.
    """

    # Initially generate a random playerA and playerB
    playerA = get_rand_player()
    playerB = get_rand_player()

    playerA_hits = get_player_stats(playerA['id'])


    # Generate a new random playerA with valid hits
    while playerA_hits == "Get New Player":
        playerA = get_rand_player()
        playerA_hits = get_player_stats(playerA['id'])

    playerB_hits = get_player_stats(playerB['id'])

    # Generate a new random playerB with valid hits that is NOT the same player as playerA
    while playerB_hits =="Get New Player" or playerB == playerA:
        playerB = get_rand_player()
        playerB_hits = get_player_stats(playerB['id'])

    return jsonify({
        'playerA': playerA['fullName'],
        'playerB': playerB['fullName'],
        'hitsA': playerA_hits,
        'hitsB': playerB_hits
    })

@hitter_bp.route('/player_images', methods=['POST'])
def player_images():
    """
    Retrieves image URLs for two players based on their names and current teams.
    Returns the image URLs for both players.
    """
    req = request.get_json()
    playerA_name = req['playerA']
    playerB_name = req['playerB']

    # Look up players and their current teams
    playerA = statsapi.lookup_player(playerA_name)
    playerB = statsapi.lookup_player(playerB_name)
    playerATeam_id = playerA[0]['currentTeam']['id']
    playerBTeam_id = playerB[0]['currentTeam']['id']
    playerATeam_name = team_names[playerATeam_id]
    playerBTeam_name = team_names[playerBTeam_id]

    # Get player images from the CSV file
    playerA_img = get_player_image(playerA[0]['fullName'], playerATeam_name)
    playerB_img = get_player_image(playerB[0]['fullName'], playerBTeam_name)

    return jsonify({
        "playerA_img": playerA_img,
        "playerB_img": playerB_img
    })

@hitter_bp.route('/check_answer', methods=['POST'])
def check_answer():
    """
    Checks the user's answer for which player has higher hits.
    Updates and returns the streak, whether the answer was correct, and the hits.
    """
    global streak
    data = request.json
    playerA = data['playerA']
    playerB = data['playerB']
    user_input = data['user_input']

    playerA_data = statsapi.lookup_player(playerA)
    playerB_data = statsapi.lookup_player(playerB)

    # Determine the player with the higher hits
    better_player = compare_hits(playerA_data, playerB_data)
    correct = False

    # Check if the user's input is correct
    if (better_player == playerA or better_player == "Equal") and user_input == "higher":
        correct = True
        streak += 1
    elif (better_player == playerB or better_player == "Equal") and user_input == "lower":
        correct = True
        streak += 1

    result = {
        'correct': correct,
        'streak': streak,
        'hitsA': f"{get_player_stats(playerA_data[0]['id'])}",
        'hitsB': f"{get_player_stats(playerB_data[0]['id'])}"
    }
    if not correct:
        result['final_streak'] = streak
        streak = 0

    return jsonify(result)

@hitter_bp.route('/next_question', methods=['POST'])
def next_question():
    """
    Provides a new random player different from the previous one, for the next question.
    Returns the new player and the previous playerA, along with their hits and the current streak.
    """
    data = request.json
    global streak
    previous_playerA = data['previous_playerA']
    previous_playerA_data = statsapi.lookup_player(previous_playerA)[0]

    # Get a new random player for playerA
    new_playerA = get_rand_player()
    new_hitsA = get_player_stats(new_playerA['id'])

    # Ensure the new random player has valid hits and is NOT the same player as the previous playerA
    while new_playerA['fullName'] == previous_playerA or new_hitsA == "Get New Player":  
        new_playerA = get_rand_player()
        new_hitsA = get_player_stats(new_playerA['id'])
    
    new_hitsB = get_player_stats(previous_playerA_data['id'])
    return jsonify({
        'newPlayerA': new_playerA['fullName'],
        'newPlayerB': previous_playerA,
        'new_hitsA': new_hitsA,
        'new_hitsB': new_hitsB,
        'streak': streak
    })

@hitter_bp.route('/end_game', methods=['POST'])
def end_game():
    """
    Ends the game, returns the final streak, and resets the streak.
    """
    global streak
    final_streak = streak
    streak = 0
    return jsonify({
        'final_streak': final_streak
    })
