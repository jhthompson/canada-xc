from collections import Counter, defaultdict
from dataclasses import dataclass

from django.db import models
from django.template.defaultfilters import floatformat
from django.urls import reverse


class Sex(models.TextChoices):
    MALE = "M", "Male"
    FEMALE = "F", "Female"
    MIXED = "X", "Mixed"

class Conference(models.Model):
    """
    A conference in a cross country league.

    For instance, the AUS.
    """

    short_name = models.CharField(max_length=10)
    full_name = models.CharField(max_length=50)
    logo = models.ImageField(upload_to="conference_logos", blank=True, null=True)

    def __str__(self):
        return self.short_name

class Team(models.Model):
    """
    A cross country team.

    For instance, the UPEI Panthers.

    This is often a school, but could also be a club or other organization.
    """

    short_name = models.CharField(max_length=12)
    full_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

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
    conferences = models.ManyToManyField(Conference)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("meet", kwargs={"year": self.date.year, "slug": self.slug})
    

@dataclass
class TeamScore:
    score: int
    scoring_members: list[tuple['Result', int]]  # (result, points)

class Race(models.Model):
    """
    A single cross country race.

    For instance, the 2024 AUS Championship's men's 10km.
    """

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
        conferences = self.meet.conferences.all()
        if conferences.count() == 1 and conferences.first().short_name == "RSEQ":
            return self.score_teams(5, 14)
        
        return self.score_teams()
    
    def top_results(self):
        return self.result_set.all().order_by('time', 'id')

    def score_teams(self, scoring_finisher_count: int = 5, maximum_team_size: int = 7):
        """
        Scores teams based on their top finishers and tracks scoring members.
        
        Returns:
            List of (team, TeamScore) tuples sorted by score ascending.
            TeamScore contains total score and list of (result, points) for scoring members.
        """
        team_results = defaultdict(list)
        team_scores = {}  # Will store TeamScore objects
                    
        results = self.top_results()
        
        # Handle manual points case
        if any(result.points is not None for result in results):
            for result in results:
                team = result.team
                if result.points is not None and len(team_results[team]) < scoring_finisher_count:
                    if team not in team_scores:
                        team_scores[team] = TeamScore(0, [])
                    team_scores[team].score += result.points
                    team_scores[team].scoring_members.append((result, result.points))
                team_results[team].append(result)
                    
            return sorted(team_scores.items(), key=lambda x: x[1].score)

        # Calculate points manually
        team_finishers_count = Counter(result.team for result in results)
        scoring_teams = {
            team for team, count 
            in team_finishers_count.items()
            if count >= scoring_finisher_count
        }
        
        points = 1
        for result in results:
            team = result.team
            
            if team in scoring_teams:
                if team not in team_scores:
                    team_scores[team] = TeamScore(0, [])
                    
                if len(team_results[team]) < scoring_finisher_count:
                    # This finisher scores points
                    team_scores[team].score += points
                    team_scores[team].scoring_members.append((result, points))
                    
                if len(team_results[team]) < maximum_team_size:
                    points += 1
                    
            team_results[team].append(result)
                                    
        return sorted(team_scores.items(), key=lambda x: x[1].score)
            
        
class Runner(models.Model):
    """
    An athlete that has competed in at least one Canadian cross country race.
    """
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    sex = models.CharField(max_length=1, choices=Sex, default=Sex.MIXED)

    birth_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("runner", kwargs={"slug": self.slug})
    
        
class RosterSpot(models.Model):
    """
    A runner's spot on a team.
    
    For instance, Jeremy Thompson's roster spot on the 2016 UPEI team.
    """
    
    runner = models.ForeignKey(Runner, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    year = models.IntegerField()
    headshot = models.ImageField(upload_to="headshots", blank=True, null=True)
    
    def __str__(self):
        return f"{self.runner} roster spot on {self.team} in {self.year}"



class Result(models.Model):
    """
    A single result from a cross country race.

    For instance, Jeremy Thompson's 35:05 finish in the 2017 AUS Championship.
    """

    race = models.ForeignKey(Race, on_delete=models.PROTECT)
    name = models.CharField(max_length=50)
    time = models.DurationField()
    team = models.ForeignKey(Team, on_delete=models.PROTECT)
    points = models.IntegerField(blank=True, null=True)
    
    runner = models.ForeignKey(Runner, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return (
            self.name
            + " - "
            + str(self.race.meet.name)
            + " "
            + str(self.race.meet.date.year)
        )
