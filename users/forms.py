import re
from django import forms
from .models import User


class RegistrationForm(forms.ModelForm):
    """Форма регистрации."""

    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    class Meta:
        model = User
        fields = ("name", "surname", "email")
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "email": "Email",
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """Форма входа."""

    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")


class EditProfileForm(forms.ModelForm):
    """Форма редактирования профиля."""

    class Meta:
        model = User
        fields = ("name", "surname", "avatar", "about", "phone", "github_url")
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "avatar": "Заменить",
            "about": "О себе",
            "phone": "Номер телефона",
            "github_url": "Ссылка на профиль GitHub",
        }

        widgets = {
            "name": forms.TextInput(),
            "surname": forms.TextInput(),
            "avatar": forms.FileInput(),
            "about": forms.Textarea(attrs={"rows": 4}),
            "phone": forms.TextInput(),
            "github_url": forms.URLInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Разрешаем оставлять поля пустыми при редактировании
        for field_name in self.fields:
            self.fields[field_name].required = False

    def clean(self):
        cleaned_data = super().clean()

        # Если поле пришло пустым, возвращаем текущее значение из БД
        for field_name in ["name", "surname", "email", "phone", "about", "github_url"]:
            if not cleaned_data.get(field_name) and hasattr(self.instance, field_name):
                cleaned_data[field_name] = getattr(self.instance, field_name)

        return cleaned_data

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone:
            phone = phone.replace(" ", "").replace("-", "")
            # Должен сохраняться только номер телефона в одном из двух форматов: либо 8XXXXXXXXXX, либо +7XXXXXXXXXX.
            if not re.match(r"^(8\d{10}|\+7\d{10})$", phone):
                raise forms.ValidationError(
                    "Введите корректный номер телефона: 8XXXXXXXXXX или +7XXXXXXXXXX!"
                )
            if phone.startswith("8"):
                phone = "+7" + phone[1:]

            # Номера телефона должны быть уникальны
            if User.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Этот номер телефона уже используется!")

        return phone

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url")
        if url and "github.com" not in url:
            raise forms.ValidationError("Ссылка должна вести на GitHub!")
        return url
