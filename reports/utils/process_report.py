import requests
import json

def process_report(report_id, boss_override=None, kb_ignore=None):
    api_url = 'https://www.warcraftlogs.com/v1/report/'
    api_key = '77c5448016dc5ecf47a9a231d338ba1d'

    print('Processing report: https://www.warcraftlogs.com/reports/{0}'.format(report_id))

    '''
    Create Fights manifest
    '''
    # Get Fights data
    fights_url = '{0}fights/{1}?api_key={2}'.format(api_url, report_id, api_key)
    response = requests.get(fights_url)
    fights_data = json.loads(response.content)

    # Build Fights Dict
    end_time = 0
    fights = {}
    for fight in fights_data['fights']:
        # Throw out non-bosses
        if fight['boss'] < 1:
            continue

        # Only include certain bosses if directed
        if boss_override:
            if fight['boss'] not in boss_override:
                continue 

        if 'size' not in fight:
            continue

        if fight['size'] == 5:
            continue

        # Add Fight data to manifest
        fights[fight['id']] = fight

        # Add Fight Time
        fights[fight['id']]['time'] = fight['end_time'] - fight['start_time']

        # Update End Time
        end_time = fight['end_time']

    '''
    Build Players manifest
    '''
    players = {}
    for player in fights_data['friendlies']:
        '''
        Skip NPCs, Players without valid fights, Pets, etc
        '''
        # Throw out fight if not in Fights manifest
        skip = False

        fight_count = 0
        for fight in player['fights']:
            if fight['id'] in fights:
                fight_count += 1

        if not fight_count:
            skip = True

        # Ignore NPCs and Pets
        if player['type'] in ['NPC', 'Pet', 'Unknown']:
            skip = True

        if skip:
            continue

        # Generate default Player manifest
        if player['name'] not in players:
            players[player['name']] = {
                'name': player['name'],
                'average_survival_percentage': 100.0,
                'death_percentages': [],
                'death_count': 0,
                'brez_count': 0,
                'hshp_count': 0,
            }

    '''
    Fetch Deaths and calculate deaths
    '''
    # Get Deaths Data
    deaths_url = '{0}tables/deaths/{1}?api_key={2}&end={3}&cutoff=4'.format(
        api_url, report_id, api_key, end_time)
    response = requests.get(deaths_url)
    deaths_data = json.loads(response.content)

    player_multiple_deaths = []
    for death in deaths_data['entries']:
        # Skip deaths not in the fights manifest
        if death['fight'] not in fights:
            continue

        fight = fights[death['fight']]

        # Increment Death Count
        players[death['name']]['death_count'] += 1

        # Skip Multiple Deaths
        '''
        So this block of code is here to ignore secondary deaths. I'm not
        sure if I agree with this, but it matches with WCL's tables so
        it's what I'm going with for now.
        '''
        if '{0}-{1}'.format(fight['id'], death['id']) in player_multiple_deaths:
            continue

        player_multiple_deaths.append('{0}-{1}'.format(fight['id'], death['id']))

        # Skip Kiling Blow Ignore list
        if 'killingBlow' in death:
            if death['killingBlow']['name'] in kb_ignore:
                continue

        # Get death time and add to players dict
        death_time = death['timestamp'] - fight['start_time']
        death_percentage = round(100 * (death_time / fight['time']), 1)

        # Append Death Percentages
        players[death['name']]['death_percentages'].append(death_percentage)

    '''
    Calculate Average Survivability
    '''
    surv_cap = len(fights) * 100.0
    for key, player in players.items():
        player_avg_surv = surv_cap
        for death in player['death_percentages']:
            player_avg_surv -= round(100.0 - death, 1)

        players[player['name']]['average_survival_percentage'] = round(
            (player_avg_surv / surv_cap) * 100, 1)

    '''
    Calculate Brez Usage
    '''
    brez_ids = [
        20484,  # Rebirth
        61999,  # Raise Ally
        20707,  # Soulstone
    ]

    for brez_id in brez_ids:
        brez_url = '{0}tables/casts/{1}?api_key={2}&end={3}&abilityid={4}&by=target&cutoff=3'.format(
            api_url, report_id, api_key, end_time, brez_id)
        response = requests.get(brez_url)
        brez_data = json.loads(response.content)

        for brez in brez_data['entries']:
            players[brez['name']]['brez_count'] += brez['total']

    '''
    Calculate Healthstone / Healing Potion usage
    '''
    cast_ids = [
        250870,  # Costal Healing Potion
        6262,    # Healthstone
    ]

    for cast_id in cast_ids:
        url = '{0}tables/casts/{1}?api_key={2}&end={3}&abilityid={4}&by=source'.format(
            api_url, report_id, api_key, end_time, cast_id)
        response = requests.get(url)
        data = json.loads(response.content)

        for entry in data['entries']:
            players[entry['name']]['hshp_count'] += entry['total']

    return players
