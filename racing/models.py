from collections import Counter, defaultdict
from operator import itemgetter

from django.db import models
from django.template.defaultfilters import floatformat
from django.urls import reverse
from django.utils.text import slugify


class Conference(models.Model):
    """
    A conference in a cross country league.

    For instance, the AUS.
    """

    short_name = models.CharField(max_length=10)
    full_name = models.CharField(max_length=50)

    def __str__(self):
        return self.short_name

class Team(models.Model):
    """
    A cross country team.

    For instance, the UPEI Panthers.

    This is often a school, but could also be a club or other organization.
    """

    short_name = models.CharField(max_length=10)
    full_name = models.CharField(max_length=50)

    def __str__(self):
        return self.short_name


class Meet(models.Model):
    """
    A cross country meet.

    For instance, the 2024 AUS Championship.
    """

    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    date = models.DateField()
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Race(models.Model):
    """
    A single cross country race.

    For instance, the 2024 AUS Championship's men's 10km.
    """
    
    class Sex(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"
        MIXED = "X", "Mixed"

    UNIT_CHOICES = [("km", "km"), ("mi", "miles")]

    meet = models.ForeignKey(Meet, on_delete=models.CASCADE)
    distance = models.DecimalField(max_digits=5, decimal_places=2)
    unit = models.CharField(choices=UNIT_CHOICES, max_length=2, default="km")
    time = models.TimeField(null=True, blank=True)
    sex = models.CharField(max_length=1, choices=Sex, default=Sex.MIXED)

    def __str__(self):
        return f"{self.meet.name} {self.distance}{self.unit} ({self.sex})"
    
    def get_display_distance(self):
        """
        Returns a human readable race distance with maximum 1 decimal place.

        :returns: A string like "5 km" or "13.1 mi".

        Example 1:

        >>> race = Race(distance=5, unit="km")
        >>> race.get_display_distance()
        "5 km"

        Example 2:

        >>> race = Race(distance=13.1094, unit="mi")
        >>> race.get_display_distance()
        "13.1 mi"
        """
        return f'{floatformat(self.distance, "-1")} {self.unit}'
    
    def top_teams(self):
        return self.score_teams()
    
    def top_results(self):
        return self.result_set.all().order_by('time')
    
    def score_teams(self, scoring_finisher_count: int = 5, maximum_team_size: int = 7):
        """
        Scores teams based on their top finishers.
        
        If any result has a points value, calculate totals based on that.
        
        Otherwise, will manually assign points totals based on the arguments.
        
        Teams are allowed a `maximum_team_size` that will score points.
        Only the top `scoring_finisher_count` finishers from each team will count towards their teams total.
        """
        
        team_results = defaultdict(list)
        team_scores = defaultdict(int)
                
        results = self.result_set.all().order_by('time')
        
        # First check for manual points totals present on results
        if any(result.points is not None for result in results):
            for result in results:
                team = result.team
                
                if result.points is not None and len(team_results[team]) < scoring_finisher_count:
                    team_scores[team] += result.points
                    
                team_results[team].append(result)  
                
            return sorted(team_scores.items(), key=itemgetter(1))

        # Otherwise, calculate points manually
        
        # 1. Count the number of finishers for each team
        team_finishers_count = Counter(result.team for result in results)
        
        # 2. Determine which teams will score points
        scoring_teams = {
            team for team, count 
            in team_finishers_count.items()
            if count >= scoring_finisher_count
        }
        
        # 3. Assign points to valid finishers
        points = 1

        for result in results:
            team = result.team
            
            if team in scoring_teams:
                if len(team_results[team]) < scoring_finisher_count:
                    # This finisher scores points for their team
                    team_scores[team] += points
                    
                if len(team_results[team]) < maximum_team_size:
                    # This finisher doesn't score for their team but still
                    # increments the points for the next finisher
                    points += 1
                    
            team_results[team].append(result)
                                    
        # 4. Sort scores by points in ascending order
        return sorted(team_scores.items(), key=itemgetter(1))
        
        
class Runner(models.Model):
    """
    An athlete that has competed in at least one Canadian cross country race.
    """
    
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    birth_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("runner", kwargs={"slug": self.slug})
    
        
class Headshot(models.Model):
    """
    A headshot of a runner.
    """
    
    runner = models.ForeignKey(Runner, on_delete=models.CASCADE, blank=True, null=True)
    image = models.ImageField(upload_to="headshots")
    year = models.IntegerField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.runner} headshot"



class Result(models.Model):
    """
    A single result from a cross country race.

    For instance, Jeremy Thompson's 35:05 finish in the 2017 AUS Championship.
    """

    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    time = models.DurationField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    points = models.IntegerField(blank=True, null=True)
    
    runner = models.ForeignKey(Runner, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return (
            self.name
            + " - "
            + str(self.race.meet.name)
            + " "
            + str(self.race.meet.date.year)
        )


