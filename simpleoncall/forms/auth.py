from django import forms

from simpleoncall.models import User


class AuthenticationForm(forms.Form):
    username = forms.CharField(
        label='Username or Email', max_length=100, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Username or Email'})
    )
    password = forms.CharField(
        label='Password', required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )


class RegistrationForm(forms.ModelForm):
    username = forms.EmailField(
        label='Email', max_length=100, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Email'})
    )
    password = forms.CharField(
        label='Password', required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )

    class Meta:
        fields = ('username', )
        model = User

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.email = user.username
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
