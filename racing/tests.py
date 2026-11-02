from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from racing.forms import HyTekUploadForm, preview_fields
from racing.hytek import parse_finish_time
from racing.models import Meet, Race, Result, Team


class HyTekUploadFormTests(TestCase):
    def test_finish_times_parse_minute_and_hour_formats(self):
        self.assertEqual(parse_finish_time("25:11"), timedelta(minutes=25, seconds=11))
        self.assertEqual(
            parse_finish_time("1:02:03.5"),
            timedelta(hours=1, minutes=2, seconds=3.5),
        )

    def test_existing_race_with_results_cannot_be_selected(self):
        meet = Meet.objects.create(
            name="Test meet", slug="test-meet", date=date(2025, 1, 1)
        )
        race = Race.objects.create(meet=meet, distance=8, sex="M")
        team = Team.objects.create(
            short_name="TEST", full_name="Test team", slug="test-team"
        )
        Result.objects.create(
            race=race, name="Runner", time=timedelta(minutes=25), team=team
        )
        form = HyTekUploadForm(
            data={"race": race.pk, "sex": "M"},
            files={"pdf": SimpleUploadedFile("results.pdf", b"pdf")},
        )

        self.assertFalse(form.is_valid())
        self.assertIn("already has results", str(form.errors["race"]))

    def test_confirm_creates_new_meet_and_race_with_parsed_date(self):
        team = Team.objects.create(
            short_name="TEST", full_name="Test team", slug="test-team"
        )
        user = get_user_model().objects.create_user("admin", is_staff=True)
        self.client.force_login(user)
        session = self.client.session
        session["hytek_rows"] = [
            {
                "name": "Runner",
                "time": "25:11",
                "points": "1",
                "raw_team": "Test team",
                "teams": [],
            }
        ]
        session["hytek_race"] = {
            "meet": "",
            "meet_name": "Test meet",
            "meet_slug": "test-meet",
            "meet_date": "2025-01-01",
            "distance": "8",
            "unit": "km",
            "sex": "M",
        }
        session.save()

        response = self.client.post(reverse("hytek_confirm"), {"team_0": team.pk})

        self.assertEqual(response.status_code, 302)
        meet = Meet.objects.get(slug="test-meet")
        self.assertEqual(meet.date, date(2025, 1, 1))
        result = meet.race_set.get().result_set.get()
        self.assertIsNone(result.runner)

    def test_preview_fields_validate_posted_team(self):
        team = Team.objects.create(
            short_name="TEST", full_name="Test team", slug="test-team"
        )
        rows = [{"raw_team": "Test team", "name": "Runner"}]
        form = preview_fields(rows, data={"team_0": str(team.pk)})

        self.assertTrue(form.is_valid(), form.errors)
