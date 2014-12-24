from django import forms

from simpleoncall.models import Team, TeamMember


class CreateTeamForm(forms.ModelForm):
    class Meta:
        fields = ('name', )
        model = Team

    def save(self, request, commit=True):
        team = super(CreateTeamForm, self).save(commit=False)

        team.owner = request.user
        if commit:
            team.save()
            request.session['team'] = {
                'id': team.id,
                'name': team.name,
            }

        tm = TeamMember()
        tm.user = request.user
        tm.team = team
        if commit:
            tm.save()

        return team


class SelectTeamForm(forms.Form):
    team = forms.ChoiceField()

    def __init__(self, data, user):
        super(SelectTeamForm, self).__init__(data)
        self.teams = dict([(t.team.id, t.team) for t in TeamMember.objects.filter(user=user)])

        new_choices = []
        for id, team in self.teams.iteritems():
            new_choices.append((id, team.name))

        self.fields['team'].choices = tuple(new_choices)

    def save(self, request, commit=True):
        team_id = self.cleaned_data['team']
        try:
            team_id = int(team_id)
        except ValueError:
            return None

        team = self.teams.get(team_id)
        if commit:
            request.session['team'] = {
                'id': team.id,
                'name': team.name,
            }
        return team
