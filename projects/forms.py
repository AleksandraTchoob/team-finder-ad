from django import forms
from .models import Project


class ProjectForm(forms.ModelForm):
    """Форма создания и редактирования проекта."""

    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        labels = {
            "name": "Название",
            "description": "Описание",
            "github_url": "Ссылка на GitHub",
            "status": "Статус",
        }
        widgets = {
            "description": forms.Textarea(
                attrs={"rows": 5, "placeholder": "Описание проекта"}
            ),
            "github_url": forms.URLInput(
                attrs={"placeholder": "https://github.com/username/repository"}
            ),
            "status": forms.Select(
                choices=[
                    ("open", "Открыт"),
                    ("closed", "Закрыт"),
                ]
            ),
        }

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url")
        if url and "github.com" not in url:
            raise forms.ValidationError("Ссылка должна вести на GitHub!")
        return url
