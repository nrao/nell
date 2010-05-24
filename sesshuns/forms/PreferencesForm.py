from django import forms
import pytz

class PreferencesForm(forms.Form):
    timeZone = forms.ChoiceField(
        choices = [(tz, tz) \
                   for tz in pytz.common_timezones], label = 'Default Time Zone')
