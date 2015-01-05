from django import forms

from simpleoncall.models import TeamSchedule


class TeamScheduleForm(forms.ModelForm):
    class Meta:
        fields = ('id', 'name', 'is_active', 'starting_time', 'rotation_duration', 'start_date', 'users')
        model = TeamSchedule

    def __init__(self, team, *args, **kwargs):
        super(TeamScheduleForm, self).__init__(*args, **kwargs)
        self.fields['users'] = forms.ModelMultipleChoiceField(queryset=team.users)
