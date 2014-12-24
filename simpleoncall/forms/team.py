from django import forms

from simpleoncall.models import Team, TeamMember


class CreateTeamForm(forms.ModelForm):
    class Meta:
        fields = ('name', )
        model = Team

    def save(self, user, commit=True):
        team = super(CreateTeamForm, self).save(commit=False)

        team.owner = user
        if commit:
            team.save()

        tm = TeamMember()
        tm.user = user
        tm.team = team
        if commit:
            tm.save()

        return team
