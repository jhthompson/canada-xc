from thefuzz import fuzz

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from racing.models import Result, Runner


class Command(BaseCommand):
    help = 'Assign Runners to Results based on name matching with fuzzy matching support'
    
    SIMILARITY_THRESHOLD = 85  # Adjust this threshold as needed

    def add_arguments(self, parser):
        parser.add_argument('race_id', type=int, help='ID of the race to filter results')

    def handle(self, *args, **kwargs):
        race_id = kwargs['race_id']
        results = Result.objects.filter(race_id=race_id, runner__isnull=True)
        
        for result in results:
            # First try exact match
            exact_matches = Runner.objects.filter(name=result.name)
            
            if exact_matches.count() == 1:
                self._assign_runner(result, exact_matches.first(), "existing")
                continue
            elif exact_matches.count() > 1:
                self._handle_multiple_matches(result, exact_matches)
                continue
                
            # Try fuzzy matching if no exact match
            fuzzy_matches = []
            all_runners = Runner.objects.all()
            
            for runner in all_runners:
                ratio = fuzz.ratio(result.name.lower(), runner.name.lower())
                if ratio >= self.SIMILARITY_THRESHOLD:
                    fuzzy_matches.append((runner, ratio))
            
            if fuzzy_matches:
                # Sort by similarity ratio descending
                fuzzy_matches.sort(key=lambda x: x[1], reverse=True)
                
                self.stdout.write(self.style.WARNING(
                    f'Found similar names for {result.name}:'
                ))
                for i, (runner, ratio) in enumerate(fuzzy_matches, start=1):
                    self.stdout.write(
                        f'{i}: {runner.name} (ID: {runner.id}, Similarity: {ratio}%)'
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
            f'Assigned {match_type} runner {runner.name} to result {result}'
        ))

    def _create_runner(self, result):
        runner = Runner.objects.create(
            name=result.name,
            slug=slugify(result.name)
        )
        self._assign_runner(result, runner, "new")

    def _handle_multiple_matches(self, result, matches):
        self.stdout.write(self.style.WARNING(f'Multiple exact matches for {result.name}:'))
        for i, runner in enumerate(matches, start=1):
            self.stdout.write(f'{i}: {runner.name} (ID: {runner.id})')
        choice = input('Enter number to select runner or press Enter to skip: ')
        
        if choice.isdigit() and 1 <= int(choice) <= matches.count():
            self._assign_runner(result, matches[int(choice)-1], "selected")
        else:
            self.stdout.write(self.style.WARNING(
                f'Skipped assigning runner to result {result}'
            ))