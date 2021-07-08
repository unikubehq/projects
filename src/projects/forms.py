from django import forms
from django.core.exceptions import ObjectDoesNotExist

from projects.models import ClusterSettings, Environment, Project


class EnvironmentForm(forms.ModelForm):

    values_path = forms.CharField(required=False)

    def clean(self):
        cleaned_data = super(EnvironmentForm, self).clean()
        try:
            deck = self.instance.deck
        except ObjectDoesNotExist:
            deck = None
        if deck and (deck.file_information and "information" in deck.file_information):
            file_paths = [file_info["path"] for file_info in deck.file_information["information"]]
            if file_paths and cleaned_data.get("values_path", None):
                if all(cleaned_data.get("values_path", None) != file_path for file_path in file_paths):
                    self.add_error("values_path", "Invalid values path.")
                else:
                    if cleaned_data["values_path"].endswith("yaml"):
                        cleaned_data["values_type"] = "file"
                    else:
                        cleaned_data["values_type"] = "dir"
        return cleaned_data

    def save(self, commit=True):
        if self.errors:
            raise ValueError(
                "The %s could not be %s because the data didn't validate."
                % (
                    self.instance._meta.object_name,
                    "created" if self.instance._state.adding else "changed",
                )
            )
        if commit:
            self.instance.save(update_project=True)
            self._save_m2m()
        else:
            self.save_m2m = self._save_m2m
        return self.instance

    class Meta:
        model = Environment
        fields = ("title", "description", "type", "deck", "sops_credentials", "values_path", "values_type", "namespace")


class ClusterSettingsForm(forms.ModelForm):
    class Meta:
        model = ClusterSettings
        fields = ("port", "project")

    def clean(self):
        cleaned_data = super(ClusterSettingsForm, self).clean()
        port = cleaned_data["port"]
        if port < 1024 or port > 65535:
            self.add_error("port", "Invalid value for port. Port must be between 1024 and 65535.")
        return cleaned_data
