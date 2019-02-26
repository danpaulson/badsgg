from django.core.management.base import BaseCommand

from reports.utils.combine_reports import combine_reports
from reports.utils.process_report import process_report

class Command(BaseCommand):
    def handle(self, *args, **options):
        report_ids = [
            '4YZfF6aPBdXL7R1c',
            'cd9DaKgn4RAYXfmT',
            'nzYp2ykBPmG9H3rx',
            'Xh4ZKwgH8Qpb1cRn',
            'RkKtYpj2Afn9ydrX',
            'wLyJDcbh1FmZxM2v',
            'F1P6Mchv8rn7ybdg'
        ]
        reports = []

        # Disable this block to view all data
        # boss_override = [
        #     2265,  # Champ
        #     2266,  # Jadefire
        #     2271,  # Opulence
        #     2268,  # Conclave
        # ]
        boss_override = None

        # Killing Blow Ignore List
        kb_ignore = ["Thief's Bane", "Melee"]

        # Process reports
        for report_id in report_ids:
            reports.append(process_report(report_id, boss_override, kb_ignore))

        players = combine_reports(reports)

        for name, player in players.items():
            sum_survival = sum(player['average_survival_percentage'])
            length_survival = float(len(player['average_survival_percentage']))
            print('{0},{1},{2},{3},{4}'.format(
                player['name'],
                round(sum_survival / length_survival, 1),
                player['death_count'],
                player['brez_count'],
                player['hshp_count'],
            ))

