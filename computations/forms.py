import math
from django.contrib.auth.forms import AuthenticationForm
from users.models import User
from django import forms
from computations.models import OptimizationModel, OptimizationMethodChoices
from django.core.exceptions import ValidationError


class AuthForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {
                "label": "Логин",
                "placeholder": "Введите логин",
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "label": "Пароль",
                "placeholder": "Введите пароль",
            }
        )

    def get_invalid_login_error(self):
        return ValidationError("Неверный имя пользователя или пароль")

    def clean(self):
        super().clean()
        username = self.cleaned_data.get("username")
        user = User.objects.filter(email=username).first()
        if user and not user.is_can_access:
            self.add_error(None, "Нет прав для входа")
        return self.cleaned_data


class ComputationForm(forms.ModelForm):
    alpha = forms.FloatField(
        label="Альфа",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        initial=1,
    )

    beta = forms.FloatField(
        label="Бета",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        initial=1,
    )

    gamma = forms.FloatField(
        label="Гамма",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        initial=1,
    )

    h = forms.FloatField(
        label="H",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        initial=9,
    )

    n = forms.FloatField(
        label="N",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        initial=10,
    )

    l_min = forms.FloatField(
        label="Нижняя граница L",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        initial=2,
    )

    l_max = forms.FloatField(
        label="Верхняя граница L",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        initial=15,
    )

    s_min = forms.FloatField(
        label="Нижняя граница S",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        initial=1,
    )

    s_max = forms.FloatField(
        label="Верхняя граница S",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        initial=12,
    )

    sum_constraint = forms.FloatField(
        label="Граница суммы L + S",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        initial=12,
    )
    computation_model = forms.ChoiceField(
        label="Метод оптимизации",
        choices=OptimizationMethodChoices.CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        initial=OptimizationMethodChoices.GRADIENT,
    )

    class Meta:
        model = OptimizationModel
        fields = [
            "alpha",
            "beta",
            "gamma",
            "h",
            "n",
            "l_min",
            "l_max",
            "s_min",
            "s_max",
            "sum_constraint",
            "computation_model",
        ]
