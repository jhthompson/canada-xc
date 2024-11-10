from thefuzz import fuzz

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from racing.models import Result, Runner


class Command(BaseCommand):
    help = 'Assign Runners to Results based on name matching with fuzzy matching support'
    
    SIMILARITY_THRESHOLD = 75

    def add_arguments(self, parser):
        parser.add_argument('race_id', type=int, help='ID of the race to filter results')

    def _check_sex_match(self, result, runner):
        if result.race.sex != runner.sex:
            self.stdout.write(self.style.WARNING(
                f'Sex mismatch - Result: {result.sex}, Runner: {runner.sex}'
            ))
            return False
        return True

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
            
            for runner in all_runners:
                ratio = fuzz.ratio(result.name.lower(), runner.name.lower())
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