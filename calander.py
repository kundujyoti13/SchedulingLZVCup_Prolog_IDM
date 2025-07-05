import os
import re
def write_database(data, instance_file):
    with open(instance_file, 'w') as file:
        for each in data:
            team, slot, value = each
            file.write(f"availability({team}, {slot}, {value}).")

def read_availabilities(availability_file):
    availabilities = []

    with open(availability_file, 'r') as file:
        availability_str = file.read()
        available_list = re.findall(r"availability\((\d+),\s*(\d+),\s*(\d+)\)", availability_str)
        availabilities = [[int(x), int(y), int(z)] for x, y, z in available_list]

    return availabilities

def read_matches(matches_file):
    matches = []

    with open(matches_file, 'r') as file:
        for line in file:
            values = line.strip().split('\t')
            row_num = len(matches) + 1
            for col_num, value in enumerate(values):
                if value != '-1':
                    match = [row_num, col_num + 1, int(value)]
                    matches.append(match)

    return matches

def compare_matches_availabilities(matches, availabilities):
    availabilities_list = []  # List to store availabilities

    for match in matches:
        team1, team2, slot = match

        team1_availabilities = [availability for availability in availabilities if availability[0] == team1 and availability[1] == slot]
        team2_availabilities = [availability for availability in availabilities if availability[0] == team2 and availability[1] == slot]

        if team1_availabilities:
            availabilities_list.extend(team1_availabilities)

        if team2_availabilities:
            availabilities_list.extend(team2_availabilities)

    return availabilities_list


matches_folder = 'calanderTestInput'
instance_folder = 'instances_asp'
output_folder = 'calanderInstance'

# Iterate over the files in the matches folder
for filename in os.listdir(matches_folder):
    if filename.endswith('.dat'):
        # Construct the full file paths
        matches_file = os.path.join(matches_folder, filename)
        calendar_name = os.path.splitext(filename)[0]
        calendar_name = calendar_name.replace('calendar_', '')
        calendar_name = calendar_name.split('_')[0]
        instance_file = os.path.join(instance_folder, f"instance{calendar_name}.lp")
        output_file = os.path.join(output_folder, f"calander_instance{calendar_name}.lp")

        # Read matches and availabilities from files
        matches = read_matches(matches_file)
        availabilities = read_availabilities(instance_file)

        # Compare matches and availabilities
        availabilities_list = compare_matches_availabilities(matches, availabilities)

        # Write availabilities to output file
        write_database(availabilities_list, output_file)
