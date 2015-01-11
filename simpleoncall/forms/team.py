from django import forms
from django.core.validators import validate_email

from simpleoncall.models import Team, TeamMember, APIKey, TeamInvite, User
from simpleoncall.mail import send_invite_mail


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

        api_key = APIKey(
            team=team,
            created_by=request.user,
        )
        if commit:
            api_key.save()

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


class InviteTeamForm(forms.Form):
    emails = forms.CharField(label='Emails (separate by ",")', widget=forms.Textarea)

    def clean_emails(self):
        raw_emails = self.cleaned_data['emails'].split(',')
        emails = []
        for email in raw_emails:
            email = email.strip('\r\n ')
            validate_email(email)
            emails.append(email)
        return emails

    def save(self, request, commit=True):
        emails = self.cleaned_data['emails']

        existing_invites = 0
        new_invites = []
        for email in emails:
            # invite already sent?
            existing_invite = TeamInvite.objects.filter(team=request.team, email=email)
            if existing_invite:
                existing_invites += 1
                continue

            # user exist and already a member?
            user = User.objects.filter(email=email)
            if user:
                team_member = TeamMember.objects.filter(user=user, team=request.team)
                if team_member:
                    existing_invites += 1
                    continue

            invite = TeamInvite(team=request.team, email=email, created_by=request.user)
            invite.save()
            new_invites.append(invite)

        if new_invites:
            success_invites = send_invite_mail(new_invites)
        else:
            success_invites = 0
        failed_invites = len(new_invites) - (success_invites or 0)
        return success_invites, existing_invites, failed_invites
