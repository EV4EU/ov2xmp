from django import forms
from idtag.models import IdTag
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field


class IdTagForm(forms.ModelForm):

    helper = FormHelper()
    helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))
    helper.form_method = 'POST'

    class Meta:
        model = IdTag
        fields = ["idToken", "expiry_date", "revoked", "user"]
    
    def __init__(self, *args, **kwargs):
        super(IdTagForm, self).__init__(*args, **kwargs)
        self.fields["expiry_date"].label = "Expiration date"
        self.fields["idToken"].label = "ID Token"
        self.fields["user"].label = "Associated user"

