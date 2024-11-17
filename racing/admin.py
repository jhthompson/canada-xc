from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.forms import ConfirmImportForm, ImportForm
from import_export.widgets import ForeignKeyWidget
from sorl.thumbnail.admin import AdminImageMixin

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect

from racing.models import (
    Conference,
    Meet,
    OfficialResult,
    Race,
    Result,
    RosterSpot,
    Runner,
    Team,
)


@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display = ("short_name", "full_name", "logo")

class RosterSpotInline(AdminImageMixin, admin.TabularInline):
    model = RosterSpot
    extra = 1
    
class ResultInline(admin.TabularInline):
    model = Result
    extra = 0

@admin.register(Runner)
class RunnerAdmin(admin.ModelAdmin):
    inlines = [RosterSpotInline, ResultInline]
    list_display = ("name", "sex", "birth_date")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("short_name", "full_name", "division")

class RaceInline(admin.TabularInline):
    model = Race
    extra = 1

@admin.register(Meet)
class MeetAdmin(admin.ModelAdmin):
    inlines = [RaceInline]
    list_display = ("name", "date")
    prepopulated_fields = {"slug": ("name",)}

class OfficialResultInline(admin.TabularInline):
    model = OfficialResult
    extra = 1

class ResultInline(admin.TabularInline):
    model = Result
    extra = 1

@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    inlines=[OfficialResultInline, ResultInline]
    search_fields = ["meet__name"]


class ResultImportForm(ImportForm):
    """Customized ImportForm, with race field required"""

    race = forms.ModelChoiceField(
        queryset=Race.objects.all(),
        required=True,
        widget=AutocompleteSelect(Result._meta.get_field("race"), admin.site),
    )


class ResultConfirmImportForm(ConfirmImportForm):
    """Customized ConfirmImportForm, with race field required"""

    race = forms.ModelChoiceField(
        queryset=Race.objects.all(),
        required=True,
        widget=AutocompleteSelect(Result._meta.get_field("race"), admin.site),
    )


class ResultResource(resources.ModelResource):
    team = fields.Field(
        column_name="team", 
        attribute="team",
        widget=ForeignKeyWidget(Team, "full_name"),
    )

    def before_import_row(self, row, **kwargs):
        race_id = kwargs["form"].cleaned_data["race"].id
        row["race"] = race_id  # set race_id for the row

    class Meta:
        model = Result


@admin.register(Result)
class RaceResultAdmin(ImportExportModelAdmin):
    model = Result

    resource_classes = [ResultResource]
    import_form_class = ResultImportForm
    confirm_form_class = ResultConfirmImportForm

    def get_import_data_kwargs(self, request, *args, **kwargs):
        """
        Prepare kwargs for import_data.
        """
        form = kwargs.get("form")
        if form and hasattr(form, "cleaned_data"):
            kwargs.update({"race": form.cleaned_data.get("race", None)})
        return kwargs

    def after_init_instance(self, instance, new, row, **kwargs):
        if "race" in kwargs:
            instance.race = kwargs["race"]

    def get_confirm_form_initial(self, request, import_form):
        initial = super().get_confirm_form_initial(request, import_form)
        # Pass on the `race` value from the import form to
        # the confirm form (if provided)
        if import_form:
            initial["race"] = import_form.cleaned_data["race"].id
        return initial
