import unicodedata

from thefuzz import fuzz

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from racing.models import Result, RosterSpot, Runner


class Command(BaseCommand):
    help = 'Assign Runners to Results based on name matching with fuzzy matching support'
    
    SIMILARITY_THRESHOLD = 75

    def add_arguments(self, parser):
        parser.add_argument('race_id', type=int, help='ID of the race to filter results')

    def _check_sex_match(self, result: Result, runner: Runner):
        if result.race.sex != runner.sex:
            self.stdout.write(self.style.WARNING(
                f'Sex mismatch - Result: {result.sex}, Runner: {runner.sex}'
            ))
            return False
        
        return True
    
    def _check_team_match(self, result: Result, runner: Runner):
        """Check if runner has roster spot matching result team/year"""
        year = result.race.meet.date.year
        roster_spot = RosterSpot.objects.filter(
            runner=runner,
            year=year
        ).first()

        if roster_spot and roster_spot.team != result.team:
            self.stdout.write(self.style.WARNING(
                f'Team mismatch - Result team: {result.team}, '
                f'Roster team: {roster_spot.team} ({year})'
            ))
            return False
        
        return True
    
    def _create_roster_spot(self, result: Result, runner: Runner):
        """Create roster spot for runner on result team/year"""
        year = result.race.meet.date.year
        roster_spot = RosterSpot.objects.create(
            runner=runner,
            team=result.team,
            year=year
        )
        self.stdout.write(self.style.SUCCESS(
            f'Created roster spot for {runner.name} on {result.team} ({year})'
        ))
        return roster_spot

    def _normalize_text(self, text: str) -> str:
        """Normalize unicode text by removing accents and converting to lowercase."""
        return unicodedata.normalize('NFKD', text.lower()).encode('ASCII', 'ignore').decode('ASCII')

    def handle(self, *args, **kwargs):
        race_id = kwargs['race_id']
        results = Result.objects.filter(race_id=race_id, runner__isnull=True)
        
        for result in results:
            # First try exact match
            exact_matches = Runner.objects.filter(name=result.name)
            
            if exact_matches.count() == 1:
                runner = exact_matches.first()
                if self._check_sex_match(result, runner):
                    self._assign_runner(result, runner, "existing")
                continue
            elif exact_matches.count() > 1:
                filtered_matches = [r for r in exact_matches if r.sex == result.race.sex]
                if filtered_matches:
                    self._handle_multiple_matches(result, filtered_matches)
                else:
                    self.stdout.write(self.style.WARNING(
                        f'Multiple matches found but none match sex ({result.race.sex}) for {result.name}'
                    ))
                continue
                
            # Try fuzzy matching if no exact match
            fuzzy_matches = []
            all_runners = Runner.objects.filter(sex=result.race.sex)
            normalized_result_name = self._normalize_text(result.name)
            
            for runner in all_runners:
                normalized_runner_name = self._normalize_text(runner.name)
                ratio = fuzz.ratio(normalized_result_name, normalized_runner_name)
                if ratio >= self.SIMILARITY_THRESHOLD:
                    fuzzy_matches.append((runner, ratio))
            
            if fuzzy_matches:
                # Sort by similarity ratio descending
                fuzzy_matches.sort(key=lambda x: x[1], reverse=True)
                
                self.stdout.write(self.style.WARNING(
                    f'Found similar names for {result.name} ({result.race.sex}):'
                ))
                for i, (runner, ratio) in enumerate(fuzzy_matches, start=1):
                    self.stdout.write(
                        f'{i}: {runner.name} (ID: {runner.id}, Sex: {runner.sex}, Similarity: {ratio}%)'
                    )
                
                choice = input(
                    'Enter number to select matching runner, "n" to create new, '
                    'or press Enter to skip: '
                )
                
                if choice.isdigit() and 1 <= int(choice) <= len(fuzzy_matches):
                    self._assign_runner(result, fuzzy_matches[int(choice)-1][0], "fuzzy-matched")
                elif choice.lower() == 'n':
                    self._create_runner(result)
                else:
                    self.stdout.write(self.style.WARNING(
                        f'Skipped assigning runner to result {result}'
                    ))
            else:
                self._create_runner(result)

    def _assign_runner(self, result, runner, match_type):
        # Check/create roster spot
        year = result.race.meet.date.year
        roster_spot = RosterSpot.objects.filter(
            runner=runner,
            year=year
        ).first()

        if not roster_spot:
            roster_spot = self._create_roster_spot(result, runner)
        elif roster_spot.team != result.team:
            self.stdout.write(self.style.WARNING(
                f'Not assigning - Team mismatch for {runner.name}: '
                f'Result team: {result.team}, Roster team: {roster_spot.team} ({year})'
            ))
            return

        result.runner = runner
        result.save()
        self.stdout.write(self.style.SUCCESS(
            f'Assigned {match_type} runner {runner.name} ({runner.sex}) to result {result}'
        ))

    def _create_runner(self, result):
        runner = Runner.objects.create(
            name=result.name,
            slug=slugify(result.name),
            sex=result.race.sex
        )
        self._create_roster_spot(result, runner)
        self._assign_runner(result, runner, "new")

    def _handle_multiple_matches(self, result, matches):
        self.stdout.write(self.style.WARNING(f'Multiple exact matches for {result.name}:'))
        for i, runner in enumerate(matches, start=1):
            self.stdout.write(f'{i}: {runner.name} (ID: {runner.id}, Sex: {runner.sex})')
        choice = input('Enter number to select runner or press Enter to skip: ')
        
        if choice.isdigit() and 1 <= int(choice) <= len(matches):
            self._assign_runner(result, matches[int(choice)-1], "selected")
        else:
            self.stdout.write(self.style.WARNING(
                f'Skipped assigning runner to result {result}'
            ))