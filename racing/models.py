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
    
    class Division(models.TextChoices):
        USPORTS = "USPORTS", "U Sports"
        CLUB = "CLUB", "Club"
        HIGH_SCHOOL = "HS", "High School"
    
    division = models.CharField(max_length=10, choices=Division, default=Division.CLUB)

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
    displacers: list[tuple['Result', int]]  # (result, points)

class Race(models.Model):
    """
    A single cross country race.

    For instance, the 2024 AUS Championship's men's 10km.
    """

    UNIT_CHOICES = [("km", "km"), ("mi", "miles")]
    TYPE_CHOICES = [("OPEN", "Open"), ("USPORTS", "U Sports")]

    meet = models.ForeignKey(Meet, on_delete=models.CASCADE)
    distance = models.DecimalField(max_digits=5, decimal_places=2)
    unit = models.CharField(choices=UNIT_CHOICES, max_length=2, default="km")
    time = models.TimeField(null=True, blank=True)
    sex = models.CharField(max_length=1, choices=Sex, default=Sex.MIXED)
    
    scorers = models.IntegerField(default=5)
    displacers = models.IntegerField(default=2)
    
    type = models.CharField(choices = TYPE_CHOICES, max_length=50, default="OPEN")

    def __str__(self):
        return f"{self.meet.name} {self.distance}{self.unit} ({self.sex})"
    
    def get_absolute_url(self):
        return reverse("race", kwargs={"year": self.meet.date.year, "slug": self.meet.slug, "race_info": (int(self.distance), self.unit, self.sex)})
    
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
        return self.result_set.all().order_by('time', 'id')

    def score_teams(self):
        """
        Scores teams and tracks scoring members + displacers.
        Only scores USPORTS teams if race type is USPORTS.
        """
        scoring_finisher_count = self.scorers
        maximum_team_size = scoring_finisher_count + self.displacers
        
        team_results = defaultdict(list)
        team_scores = {}
                    
        results = self.top_results()
        
        # Handle manual points case 
        if any(result.points is not None for result in results):
            for result in results:
                team = result.team
                if result.points is not None:
                    if team not in team_scores:
                        team_scores[team] = TeamScore(0, [], [])
                    if len(team_results[team]) < scoring_finisher_count:
                        team_scores[team].score += result.points
                        team_scores[team].scoring_members.append((result, result.points))
                    elif len(team_results[team]) < maximum_team_size:
                        team_scores[team].displacers.append((result, result.points))
                team_results[team].append(result)
                    
            return sorted(team_scores.items(), key=lambda x: x[1].score)

        # Calculate points manually
        team_finishers_count = Counter(result.team for result in results)
        
        # Filter for USPORTS teams if race type is USPORTS
        scoring_teams = set()
        for team, count in team_finishers_count.items():
            if count >= scoring_finisher_count:
                if self.type == "USPORTS" and team.division != Team.Division.USPORTS:
                    continue
                scoring_teams.add(team)
        
        # Rest of scoring logic remains the same
        points = 1
        for result in results:
            team = result.team
            
            if team in scoring_teams:
                if team not in team_scores:
                    team_scores[team] = TeamScore(0, [], [])
                    
                if len(team_results[team]) < scoring_finisher_count:
                    # This finisher scores points
                    team_scores[team].score += points
                    team_scores[team].scoring_members.append((result, points))
                elif len(team_results[team]) < maximum_team_size:
                    # This finisher is a displacer
                    team_scores[team].displacers.append((result, points))
                    
                if len(team_results[team]) < maximum_team_size:
                    points += 1
                    
            team_results[team].append(result)
                                    
        return sorted(team_scores.items(), key=lambda x: x[1].score)

class OfficialResult(models.Model):
    """
    A link to a race's official results
    """
    
    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, default="Official Results")
    link = models.URLField()
        
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
