from django import forms

from simpleoncall.models import User


class EditAccountForm(forms.ModelForm):
    username = forms.EmailField(
        label='Email', max_length=100, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Email'})
    )
    first_name = forms.CharField(
        label='First Name', max_length=100, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        label='Last Name', max_length=100, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )

    class Meta:
        fields = ('username', 'first_name', 'last_name')
        model = User

    def save(self, commit=True):
        user = super(EditAccountForm, self).save(commit=False)
        user.email = user.username
        if commit:
            user.save()
        return user


class ChangePasswordForm(forms.ModelForm):
    password_1 = forms.CharField(
        label='Password', required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )
    password_2 = forms.CharField(
        label='Re-Type Password', required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Re-Type Password'})
    )

    class Meta:
        fields = tuple()
        model = User

    def save(self, commit=True):
        user = super(ChangePasswordForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password_1'])
        if commit:
            user.save()
        return user
