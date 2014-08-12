from django.forms import ModelForm
from models import Assessment,SpatialUnitType
import django.db
from django.db import models


class AssessmentForm(ModelForm):
    """

    """

    class Meta:
        model = Assessment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        sut = django.db.models.ForeignKey(SpatialUnitType)
        self.fields['new_field']=sut








