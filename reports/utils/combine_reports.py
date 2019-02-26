def combine_reports(reports):
    players = {}
    for report in reports:
        for name, player in report.items():
            if name not in players:
                players[name] = {
                    'name': name,
                    'average_survival_percentage': [],
                    'death_percentages': [],
                    'death_count': 0,
                    'brez_count': 0,
                    'hshp_count': 0,
                }

            players[name]['average_survival_percentage'].append(
                player['average_survival_percentage'])

            players[name]['death_percentages'] += player['death_percentages']
            players[name]['death_count'] += player['death_count']
            players[name]['brez_count'] += player['brez_count']
            players[name]['hshp_count'] += player['hshp_count']

    return players
