import requests
import json

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Get Fights
        fights_url = 'https://www.warcraftlogs.com/v1/report/fights/4YZfF6aPBdXL7R1c?api_key=77c5448016dc5ecf47a9a231d338ba1d' 
        response = requests.get(fights_url)
        fights_data = json.loads(response.content)

        # Build Fights Dict
        fights = {}
        for fight in fights_data['fights']:
            fights[fight['id']] = fight

            # Add Fight Time
            fights[fight['id']]['time'] = fight['end_time'] - fight['start_time']

        '''
        TODO: Generate Participation tables from fights for accurate survivability caps
        '''

        # Get Deaths
        death_url = 'https://www.warcraftlogs.com/v1/report/tables/deaths/4YZfF6aPBdXL7R1c?api_key=77c5448016dc5ecf47a9a231d338ba1d&end=8509056&cutoff=4'
        response = requests.get(death_url)

        deaths_data = json.loads(response.content)

        players = {}
        average_cap = len(fights) * 100
        for death in deaths_data['entries']:
            fight = fights[death['fight']]
            name = death['name']

            # Get death time
            death_time = death['timestamp'] - fight['start_time']
            death_percentage = round(100 * (death_time / fight['time']), 1)

            # Get Fight MS
            if name not in players:
                players[name] = {
                    'name': name,
                    'death_percentages': [],
                }

            players[name]['death_percentages'].append(death_percentage)

        surv_cap = 29 * 100.0
        for key, player in players.items():
            player_avg_surv = surv_cap
            for death in player['death_percentages']:
                player_avg_surv -= round(100.0 - death, 1)

            print('{0} ({1})'.format(player['name'], round(player_avg_surv / 2900 * 100, 1)))
            print('Death Percentages: {0}'.format(player['death_percentages']))
