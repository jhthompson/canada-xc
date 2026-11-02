from django import forms

from racing.models import Meet, Race, Sex, Team


class HyTekUploadForm(forms.Form):
    pdf = forms.FileField()

    def clean_pdf(self):
        pdf = self.cleaned_data["pdf"]
        if pdf.size > 20 * 1024 * 1024:
            raise forms.ValidationError("PDF must be 20 MB or smaller.")
        if not pdf.read(1024).lstrip().startswith(b"%PDF-"):
            raise forms.ValidationError("Upload a valid PDF file.")
        pdf.seek(0)
        return pdf

    race = forms.ModelChoiceField(
        queryset=Race.objects.select_related("meet").order_by("-meet__date"),
        required=False,
    )
    meet = forms.ModelChoiceField(
        queryset=Meet.objects.order_by("-date"), required=False
    )
    meet_name = forms.CharField(max_length=50, required=False)
    meet_slug = forms.SlugField(required=False)
    meet_date = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"type": "date"})
    )
    distance = forms.DecimalField(max_digits=5, decimal_places=2, required=False)
    unit = forms.ChoiceField(choices=Race.UNIT_CHOICES, required=False)
    sex = forms.ChoiceField(choices=Sex.choices)

    def clean(self):
        data = super().clean()
        if data.get("race"):
            data["sex"] = data["race"].sex
            if data["race"].result_set.exists():
                self.add_error(
                    "race", "This race already has results; imports are blocked."
                )
            return data
        if not data.get("meet") and not all(
            data.get(key) for key in ("meet_name", "meet_slug", "meet_date")
        ):
            self.add_error(None, "Choose a meet or provide its name, slug, and date.")
        if not data.get("distance") or not data.get("unit"):
            self.add_error(None, "A distance and unit are required for a new race.")
        return data


class HyTekPreviewForm(forms.Form):
    pass


def preview_fields(rows, data=None, initial=None):
    form = HyTekPreviewForm(data=data, initial=initial or {})
    for index, row in enumerate(rows):
        form.fields[f"team_{index}"] = forms.ModelChoiceField(
            queryset=Team.objects.all().order_by("full_name"),
            required=True,
            label=f"Team for {row['raw_team']}",
        )
    return form
