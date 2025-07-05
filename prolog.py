import re

def generate_match_table(matches, team_count):
    table = [[" " for _ in range(team_count + 1)] for _ in range(team_count + 1)]

    # Set the headers
    table[0] = [" ", *[str(i) for i in range(1, team_count + 1)]]

    for i in range(1, team_count + 1):
        table[i][0] = str(i)

    # Populate the table with match data
    for match in matches:
        home_team, away_team, slot = match
        table[home_team][away_team] = str(slot)

    # Fill empty slots with -1
    for i in range(1, team_count + 1):
        for j in range(1, team_count + 1):
            if table[i][j] == " ":
                table[i][j] = "-1"

    # Print the table
    print_table(table)


def print_table(table):
    col_width = max(len(str(cell)) for row in table for cell in row) + 2

    for row in table:
        print("|", end="")
        for cell in row:
            print(f"{str(cell):^{col_width}}|", end="")
        print("\n" + "-" * (col_width * len(row) + len(row) + 1))



def process_output(matches, availability_str):
    matches_list = [tuple(map(int, re.findall(r'\d+', s))) for s in matches]
    matches_list = [[int(x), int(y), int(z)] for x, y, z in matches_list]
    match_count = len(matches_list)
    print(f"Number of matches found: {match_count}\n")

    available_list = re.findall(r"availability\((\d+),\s*(\d+),\s*(\d+)\)", availability_str)
    available_list = [[int(x), int(y), int(z)] for x, y, z in available_list]

    availability_dict = {}

    for team, slot, availability in available_list:
        team = int(team)
        slot = int(slot)
        availability = int(availability)

        if team not in availability_dict:
            availability_dict[team] = {}

        availability_dict[team][slot] = availability

    slots_set = set()
    repeated_slots = []
    duplicate_matches = set()

    team_games = {}  # Dictionary to track number of games for each team

    for i in range(len(matches_list)):
        home, away, slot = matches_list[i]
        match_tuple = (home, away)

        if slot in slots_set and slot not in repeated_slots:
            repeated_slots.append(slot)
        else:
            slots_set.add(slot)

        if match_tuple in duplicate_matches:
            print(f'Duplicate match found: {matches_list[i]} \n')
            # Handle duplicate match logic here
        else:
            for j in range(i + 1, len(matches_list)):
                if home == matches_list[j][0] and away == matches_list[j][1] and slot != matches_list[j][2]:
                    duplicate_matches.add(match_tuple)
                    duplicate_matches.add((home, away, matches_list[j][2]))
                    print(f'Duplicate matches found with different slots: {matches_list[i]} and {matches_list[j]} \n')

        # Track number of games for each team
        if home not in team_games:
            team_games[home] = 1
        else:
            team_games[home] += 1

        if away not in team_games:
            team_games[away] = 1
        else:
            team_games[away] += 1

    if repeated_slots:
        print("Repeated slots found: \n", repeated_slots)
        print("\n")
    else:
        print("No repeated slots found. \n")

    for home, away, slot in matches_list:
        if home in availability_dict and slot in availability_dict[home]:
            if availability_dict[home][slot] == 1:
                pass
            elif availability_dict[home][slot] == 0:
                print(f'{home} is not playing in home slot in {home},{away},{slot} \n')
                pass
            elif availability_dict[home][slot] == 2:
                print(f'{home} is playing in a forbidden slot in {home},{away},{slot} \n')
                pass

            # Check if any other matches are scheduled for the home team on the same slot
            other_home_matches = [match for match in matches_list if match[0] == home and match[2] == slot]
            if len(other_home_matches) > 1:
                print(f'Team {home} has other matches scheduled on the same slot in {other_home_matches} \n')

        if away in availability_dict and slot in availability_dict[away]:
            if availability_dict[away][slot] == 0:
                pass
            elif availability_dict[away][slot] == 1:
                #print(f'{away} is playing in a home slot in {home},{away},{slot} \n')
                pass
            elif availability_dict[away][slot] == 2:
                print(f'{away} is playing in a forbidden slot in {home},{away},{slot} \n')
                pass

            # Check if any other matches are scheduled for the away team on the same slot
            other_away_matches = [match for match in matches_list if match[1] == away and match[2] == slot]
            if len(other_away_matches) > 1:
                print(f'Team {away} has other matches scheduled on the same slot in {other_away_matches} \n')

    team_count = len(availability_dict)
    generate_match_table(matches_list, team_count)


def file_to_list(file_path):
    try:
        with open(file_path, 'r') as file:
            file_content = file.readlines()
            content_list = [line.strip() for line in file_content]
        return content_list
    except FileNotFoundError:
        print("File not found!")
        return []

# Usage example
file_path = './Prolog_output.txt'
result_list = file_to_list(file_path)
with open('./instances/instance1.lp', 'r') as file:
                available_str = file.read()
                process_output(result_list, available_str)

