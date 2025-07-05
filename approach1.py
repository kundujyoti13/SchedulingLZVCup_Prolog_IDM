from subprocess import PIPE, Popen
import multiprocessing
import re
import glob
import os 
import sys
from concurrent.futures import ProcessPoolExecutor

list=[]
def run_clingo(program_file, instance_file, timeout):
    num_threads = multiprocessing.cpu_count()
    command = ["clingo", "-t", str(num_threads), "--time-limit", str(timeout), program_file, instance_file]
    
    try:
        process = Popen(command, stdout=PIPE, stderr=PIPE, text=True, bufsize=0)

        # Read and capture the output of the subprocess
        output, _ = process.communicate()
    except Exception as e:
        print(f"An error occurred: {e} \n")
        return None

    # Split the output into lines
    lines = output.strip().split('\n')

    if len(lines) == 0:
        return None  # No output within the timeout

    # Find the index of the last fully printed output
    last_output_index = len(lines) - 1
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].startswith('Answer') and i < len(lines) - 1:
            last_output_index = i
            break

    # Extract the last fully printed output
    last_output = '\n'.join(lines[last_output_index:])

    # Extract the matches from the last output
    matches = re.findall(r'match\(\d+,\d+,\d+\)', last_output)
    
    return matches

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

def process_output(matches, availability_str, Rmax, m):
    matches_list = [tuple(map(int, re.findall(r'\d+', s))) for s in matches]
    matches_list = [[int(x), int(y), int(z)] for x, y, z in matches_list]
    match_count = len(matches_list)
    print("-----------------------------------------------------------------------------------------------------------")
    print(f"Number of matches found: {match_count}\n")
    print("-----------------------------------------------------------------------------------------------------------")

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
            print("-----------------------------------------------------------------------------------------------------------")
            print(f'Duplicate match found: {matches_list[i]} \n')
            print("-----------------------------------------------------------------------------------------------------------")
            # Handle duplicate match logic here
        else:
            for j in range(i + 1, len(matches_list)):
                if home == matches_list[j][0] and away == matches_list[j][1] and slot != matches_list[j][2]:
                    duplicate_matches.add(match_tuple)
                    duplicate_matches.add((home, away, matches_list[j][2]))
                    print("-----------------------------------------------------------------------------------------------------------")
                    print(f'Duplicate matches found with different slots: {matches_list[i]} and {matches_list[j]} \n')
                    print("-----------------------------------------------------------------------------------------------------------")

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
        print("-----------------------------------------------------------------------------------------------------------")
        print("Repeated slots found with diferent teams: \n", repeated_slots)
        print("\n")
        print("-----------------------------------------------------------------------------------------------------------")
    else:
        print("-----------------------------------------------------------------------------------------------------------")
        print("No repeated slots found. \n")
        list.append("1")
        print("-----------------------------------------------------------------------------------------------------------")

    for home, away, slot in matches_list:
        if home in availability_dict and slot in availability_dict[home]:
            if availability_dict[home][slot] == 1:
                pass
            elif availability_dict[home][slot] == 0:
                print("-----------------------------------------------------------------------------------------------------------")
                print(f'{home} is playing in an away slot in {home},{away},{slot} \n')
                list.append("2")
                print("-----------------------------------------------------------------------------------------------------------")
                pass
            elif availability_dict[home][slot] == 2:
                print("-----------------------------------------------------------------------------------------------------------")
                print(f'{home} is playing in a forbidden slot in {home},{away},{slot} \n')
                list.append("2")
                print("-----------------------------------------------------------------------------------------------------------")
                pass

            # Check if any other matches are scheduled for the home team on the same slot
            other_home_matches = [match for match in matches_list if match[0] == home and match[2] == slot]
            if len(other_home_matches) > 1:
                print("-----------------------------------------------------------------------------------------------------------")
                print(f'{home} has other matches scheduled on the same slot in {other_home_matches} \n')
                list.append("1")
                list.append("4")
                print("-----------------------------------------------------------------------------------------------------------")

        if away in availability_dict and slot in availability_dict[away]:
            if availability_dict[away][slot] == 0:
                pass
            elif availability_dict[away][slot] == 1:
                # print(f'{away} is playing in a home slot in {home},{away},{slot} \n')
                pass
            elif availability_dict[away][slot] == 2:
                print("-----------------------------------------------------------------------------------------------------------")
                print(f'{away} is playing in a forbidden slot in {home},{away},{slot} \n')
                list.append("3")
                print("-----------------------------------------------------------------------------------------------------------")
                pass

            # Check if any other matches are scheduled for the away team on the same slot
            other_away_matches = [match for match in matches_list if match[1] == away and match[2] == slot]
            if len(other_away_matches) > 1:
                print("-----------------------------------------------------------------------------------------------------------")
                print(f'{away} has other matches scheduled on the same slot in {other_away_matches} \n')
                list.append("4")
                print("-----------------------------------------------------------------------------------------------------------")

    team_count = len(availability_dict)

    # Find matches within m time slots
    print("-----------------------------------------------------------------------------------------------------------")
    print(f"Matches with at least {m} time slots between two games with the same pair of teams:\n")
    list.append("6")
    print("-----------------------------------------------------------------------------------------------------------")
    team_matches = {}  # Dictionary to store the last played match slot for each team pair

    for home, away, slot in matches_list:
        pair = frozenset((home, away))
        reverse_pair = frozenset((away, home))
        if pair in team_matches or reverse_pair in team_matches:
            prev_slot = team_matches.get(pair, team_matches.get(reverse_pair))
            if abs(slot - prev_slot) <= m:
                print("-----------------------------------------------------------------------------------------------------------")
                print(f"There is a match between {home} and {away} with at least {m} time slots between two games.")
                print(f"Match details: {home}, {away}, {prev_slot}")
                print(f"Match details: {home}, {away}, {slot}\n")
                list.append("6")
                print("-----------------------------------------------------------------------------------------------------------")
        team_matches[pair] = slot

def process_output(matches, availability_str, Rmax, m):
    matches_list = [tuple(map(int, re.findall(r'\d+', s))) for s in matches]
    matches_list = [[int(x), int(y), int(z)] for x, y, z in matches_list]
    match_count = len(matches_list)
    print("-----------------------------------------------------------------------------------------------------------")
    print(f"Number of matches found: {match_count}\n")
    print("-----------------------------------------------------------------------------------------------------------")

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
            print("-----------------------------------------------------------------------------------------------------------")
            print(f'Duplicate match found: {matches_list[i]} \n')
            print("-----------------------------------------------------------------------------------------------------------")
            # Handle duplicate match logic here
        else:
            for j in range(i + 1, len(matches_list)):
                if home == matches_list[j][0] and away == matches_list[j][1] and slot != matches_list[j][2]:
                    duplicate_matches.add(match_tuple)
                    duplicate_matches.add((home, away, matches_list[j][2]))
                    print("-----------------------------------------------------------------------------------------------------------")
                    print(f'Duplicate matches found with different slots: {matches_list[i]} and {matches_list[j]} \n')
                    print("-----------------------------------------------------------------------------------------------------------")

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
        print("-----------------------------------------------------------------------------------------------------------")
        print("Repeated slots found with different teams: \n", repeated_slots)
        print("\n")
        print("-----------------------------------------------------------------------------------------------------------")
    else:
        print("-----------------------------------------------------------------------------------------------------------")
        print("No repeated slots found. \n")
        print("-----------------------------------------------------------------------------------------------------------")

    for home, away, slot in matches_list:
        if home in availability_dict and slot in availability_dict[home]:
            if availability_dict[home][slot] == 1:
                pass
            elif availability_dict[home][slot] == 0:
                print("-----------------------------------------------------------------------------------------------------------")
                print(f'{home} is playing in an away slot in {home},{away},{slot} \n')
                list.append("2")
                print("-----------------------------------------------------------------------------------------------------------")
                pass
            elif availability_dict[home][slot] == 2:
                print("-----------------------------------------------------------------------------------------------------------")
                print(f'{home} is playing in a forbidden slot in {home},{away},{slot} \n')
                list.append("2")
                print("-----------------------------------------------------------------------------------------------------------")
                pass
            

            # Check if any other matches are scheduled for the home team on the same slot
            other_home_matches = [match for match in matches_list if match[0] == home and match[2] == slot]
            if len(other_home_matches) > 1:
                print("-----------------------------------------------------------------------------------------------------------")
                print(f'Team {home} has other matches scheduled on the same slot in {other_home_matches} \n')
                list.append("1")
                list.append("4")
                print("-----------------------------------------------------------------------------------------------------------")

        if away in availability_dict and slot in availability_dict[away]:
            if availability_dict[away][slot] == 0:
                pass
            elif availability_dict[away][slot] == 1:
                # print(f'{away} is playing in a home slot in {home},{away},{slot} \n')
                pass
            elif availability_dict[away][slot] == 2:
                print("-----------------------------------------------------------------------------------------------------------")
                print(f'{away} is playing in a forbidden slot in {home},{away},{slot} \n')
                list.append("3")
                print("-----------------------------------------------------------------------------------------------------------")
                pass

            # Check if any other matches are scheduled for the away team on the same slot
            other_away_matches = [match for match in matches_list if match[1] == away and match[2] == slot]
            if len(other_away_matches) > 1:
                print("-----------------------------------------------------------------------------------------------------------")
                print(f'Team {away} has other matches scheduled on the same slot in {other_away_matches} \n')
                list.append("3")
                print("-----------------------------------------------------------------------------------------------------------")

    team_count = len(availability_dict)

    # Find matches within m time slots

    team_matches = {}  # Dictionary to store the last played match slot for each team pair

    for home, away, slot in matches_list:
        pair = frozenset((home, away))
        reverse_pair = frozenset((away, home))
        if pair in team_matches or reverse_pair in team_matches:
            prev_slot = team_matches.get(pair, team_matches.get(reverse_pair))
            if abs(slot - prev_slot) < m:
                print("-----------------------------------------------------------------------------------------------------------")
                print(f"There is a match between {home} and {away} with at least {m} time slots between two games.")
                print(f"Match details: {home}, {away}, {prev_slot}")
                print(f"Match details: {home}, {away}, {slot}\n")
                list.append("6")
                print("-----------------------------------------------------------------------------------------------------------")
            
        team_matches[pair] = slot

    for team, games in team_games.items():
        team_matches = [match for match in matches_list if match[0] == team or match[1] == team]
        if len(team_matches) > 2:
            team_matches_sorted = sorted(team_matches, key=lambda x: x[2])  # Sort matches by slot
            for i in range(len(team_matches_sorted) - 2):
                if team_matches_sorted[i + 2][2] - team_matches_sorted[i][2] <= Rmax:
                    print("-----------------------------------------------------------------------------------------------------------")
                    print(f"Team {team} has more than 2 games scheduled within{Rmax} time slots.")
                    print("Violating Match details:")
                    list.append("5")
                    print("-----------------------------------------------------------------------------------------------------------")
                    for j in range(i, i + 3):
                        match = team_matches_sorted[j]
                        print(f"{match[0]} vs {match[1]} at slot {match[2]}")
                    print()
                    break
    team_count = len(availability_dict)
    generate_match_table(matches_list, team_count)


def process_instance_files(program_file, instance_files, timeout):
    for instance_file in instance_files:
        output_folder = "approach1"
        os.makedirs(output_folder, exist_ok=True)
        file_name = "output"+instance_file[14:-3]+".txt"
        file_path = os.path.join(output_folder, file_name)
        with open(file_path, 'w') as file:
            sys.stdout = file
            print("-----------------------------------------------------------------------------------------------------------")
            print("Computing schedule for "+instance_file)
            print("-----------------------------------------------------------------------------------------------------------")
            matches = run_clingo(program_file, instance_file, timeout)
            

            if matches is not None:
                with open(instance_file, 'r') as file:
                    available_str = file.read()
                    process_output(matches, available_str,Rmax,m)
                    print("-----------------------------------------------------------------------------------------------------------")
                    if len(list)==0:
                        print("Constraint 1 Satisfied")
                        print("Constraint 2 Satisfied")
                        print("Constraint 3 Satisfied")
                        print("Constraint 4 Satisfied")
                        print("Constraint 5 Satisfied")
                        print("Constraint 6 Satisfied")
                    print("-----------------------------------------------------------------------------------------------------------")
                    print("Computed")
                    print("-----------------------------------------------------------------------------------------------------------")
                    
            sys.stdout = sys.__stdout__

instance_files = glob.glob("instances_asp/*.lp")  # Assuming the instance files are in the "instances" directory
program_file = "schedule.lp"  # Path to the Clingo program file
timeout = 1200  # Timeout value in seconds
Rmax = 4
m = 60

process_instance_files(program_file, instance_files, timeout)

