from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Логин',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите логин',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите пароль',
            'autocomplete': 'current-password',
        })
    )


class ForcePasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        label='Старый пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Текущий (временный) пароль',
        })
    )
    new_password = forms.CharField(
        label='Новый пароль',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Минимум 8 символов',
        })
    )
    confirm_password = forms.CharField(
        label='Подтверждение нового пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Повторите новый пароль',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        new_pw = cleaned_data.get('new_password')
        confirm_pw = cleaned_data.get('confirm_password')
        if new_pw and confirm_pw and new_pw != confirm_pw:
            raise forms.ValidationError('Пароли не совпадают.')
        return cleaned_data


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'bio', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'bio': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-file'}),
        }