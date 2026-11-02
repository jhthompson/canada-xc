import json
from datetime import date, timedelta
from io import StringIO
from unittest.mock import patch
from urllib.error import URLError

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse

from racing.forms import HyTekUploadForm, preview_fields
from racing.hytek import parse_finish_time
from racing.models import Meet, Race, Result, Team


class AthleticLiveImportTests(TestCase):
    url = "https://data.athletic.live/ind_res_list/_doc/2939642"

    def setUp(self):
        meet = Meet.objects.create(
            name="Test meet", slug="test", date=date(2026, 10, 31)
        )
        self.race = Race.objects.create(meet=meet, distance=8, sex="M")
        self.team = Team.objects.create(
            full_name="Guelph Gryphons", short_name="GUE", slug="guelph"
        )
        self.payload = {
            "_source": {
                "g": "Male",
                "r": [
                    {
                        "p": "1",
                        "m": "23:56.2",
                        "pt": 1,
                        "a": {"n": "Jack Lehto", "t": {"n": "Guelph Gryphons"}},
                    },
                    {
                        "p": "--",
                        "m": "DNF",
                        "pt": 0,
                        "a": {"n": "Willem De Gooyer", "t": {"n": "Guelph Gryphons"}},
                    },
                ],
            }
        }
        self.fetch = patch("racing.management.commands.import_athletic_live.urlopen")

    def run_import(self):
        with self.fetch as fetch:
            fetch.return_value.__enter__.return_value.read.return_value = json.dumps(
                self.payload
            ).encode()
            call_command(
                "import_athletic_live", self.race.pk, self.url, stdout=StringIO()
            )

    def test_imports_finish_time_and_points_and_skips_dnf(self):
        self.run_import()
        result = self.race.result_set.get()
        self.assertEqual(result.name, "Jack Lehto")
        self.assertEqual(result.time, timedelta(minutes=23, seconds=56.2))
        self.assertEqual(result.points, 1)
        self.assertEqual(result.team, self.team)
        self.assertIsNone(result.runner)

    def test_zero_points_are_not_imported_as_scoring_points(self):
        self.payload["_source"]["r"][0]["pt"] = 0
        self.run_import()
        self.assertIsNone(self.race.result_set.get().points)

    def test_refuses_repeat_import(self):
        self.run_import()
        with self.assertRaisesMessage(CommandError, "already has results"):
            self.run_import()
        self.assertEqual(self.race.result_set.count(), 1)

    def test_unknown_team_leaves_no_partial_import(self):
        self.payload["_source"]["r"].append(
            {
                "p": "2",
                "m": "24:22.3",
                "pt": 2,
                "a": {"n": "Samuel Patrick", "t": {"n": "Unknown"}},
            }
        )
        with self.assertRaisesMessage(CommandError, "Unknown"):
            self.run_import()
        self.assertFalse(Result.objects.exists())

    def test_rejects_malformed_results_and_sex_mismatch(self):
        for payload in (
            {},
            {"_source": {"g": "Female", "r": []}},
            {"_source": {"g": "Male", "r": [{}]}},
        ):
            with self.subTest(payload=payload):
                self.payload = payload
                with self.assertRaises(CommandError):
                    self.run_import()
                self.assertFalse(Result.objects.exists())

    def test_rejects_untrusted_url(self):
        with self.assertRaisesMessage(CommandError, "URL"):
            call_command(
                "import_athletic_live", self.race.pk, "https://example.com/results"
            )

    def test_fetch_identifies_client(self):
        with self.fetch as fetch:
            fetch.return_value.__enter__.return_value.read.return_value = (
                json.dumps(self.payload).encode()
            )
            call_command(
                "import_athletic_live", self.race.pk, self.url, stdout=StringIO()
            )
            request = fetch.call_args.args[0]
            self.assertEqual(request.full_url, self.url)
            self.assertEqual(request.get_header("User-agent"), "canada-xc/0.1")
            self.assertEqual(request.get_header("Accept"), "application/json")

    def test_network_failure_is_command_error(self):
        with self.fetch as fetch:
            fetch.side_effect = URLError("offline")
            with self.assertRaisesMessage(CommandError, "offline"):
                call_command("import_athletic_live", self.race.pk, self.url)


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

    def test_confirm_resolves_existing_meet_selection(self):
        meet = Meet.objects.create(
            name="AUS Championships", slug="aus", date=date(2026, 11, 1)
        )
        team = Team.objects.create(
            short_name="TEST", full_name="Test team", slug="test-team"
        )
        user = get_user_model().objects.create_user("admin", is_staff=True)
        self.client.force_login(user)
        session = self.client.session
        session["hytek_rows"] = [
            {"name": "Runner", "time": "25:11", "points": "", "raw_team": "Test team"}
        ]
        # Older pending sessions stored the meet label rather than its primary key.
        session["hytek_race"] = {
            "meet": str(meet),
            "distance": "8",
            "unit": "km",
            "sex": "F",
        }
        session.save()

        response = self.client.post(reverse("hytek_confirm"), {"team_0": team.pk})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(meet.race_set.get().sex, "F")

    def test_preview_fields_validate_posted_team(self):
        team = Team.objects.create(
            short_name="TEST", full_name="Test team", slug="test-team"
        )
        rows = [{"raw_team": "Test team", "name": "Runner"}]
        form = preview_fields(rows, data={"team_0": str(team.pk)})

        self.assertTrue(form.is_valid(), form.errors)
