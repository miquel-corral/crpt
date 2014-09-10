import django.db
from django.db import models
from django.core.exceptions import ValidationError

import datetime
from django.utils import timezone

class Common(django.db.models.Model):
    """
    Abstract class for common attributes and behaviour
    """
    name = django.db.models.CharField(max_length=200,unique=True)
    # ...
    def __unicode__(self):  # Python 3: def __str__(self):
        return self.name

    class Meta:
        abstract = True

class Responder(Common):
    """
    Represents a single responder for an assessment
    """
    organization = django.db.models.CharField(max_length=200, null=True)
    position = django.db.models.CharField(max_length=200, null=True)
    email = django.db.models.EmailField(max_length=250,null=True, unique=True)


class HazardCategory(Common):
    """
    Represents a Hazard Category
    """

class Hazard(Common):
    """
    Represents a single Hazard:

    """
    category = django.db.models.ForeignKey(HazardCategory)


class SpatialUnitType(Common):
    """
    Represents a Spatial Unit Type
    """

class City(Common):
    """
    Represents a city to be assessed

    """
    responders = django.db.models.ManyToManyField(Responder)

class Actor(Common):
    """
    Represents an actor in relation with DRR/resilience in the assessment

    """

class Role(Common):
    """
    Represents a role of an actor
    """

class Assessment(Common):
    """
    Represents an assessment for a city

    """
    initial_date = django.db.models.DateField('initial date')
    final_date  = django.db.models.DateField('final date', null=True, blank=True)
    last_update = django.db.models.DateTimeField('last update',null=True, blank=True)
    spatial_unit_name = django.db.models.CharField(max_length=200, default='City')
    short_term = django.db.models.CharField(max_length=200, null=True)
    mid_term = django.db.models.CharField(max_length=200, null=True)
    long_term = django.db.models.CharField(max_length=200, null=True)
    city = django.db.models.ForeignKey(City)
    hazards = django.db.models.ManyToManyField(Hazard)
    spatial_unit_type = django.db.models.ForeignKey(SpatialUnitType)
    actors = django.db.models.ManyToManyField(Actor)

    def clean(self):
        # Control initial date is informed right (required field)
        if(self.initial_date is not None and self.initial_date < datetime.date.today()):
            raise ValidationError('Initial date should be today or forward in time.')
        # Control initial and final dates
        if(self.initial_date is not None and self.final_date is not None):
            print("Diff. Dates: {}".format((self.initial_date - self.final_date).days))
            if (self.initial_date - self.final_date).days > 0:
                raise ValidationError('Final date should be forward in time than initial date.')
        # Control 'New Assessment' name is not allowed
        if(self.name == 'New Assessment'):
            raise ValidationError('"New Assessment" not allowed as Assessment name.')


class ActorRole(Common):
    """
    Represents roles for actors in relation of hazards of an assessment

    """
    assessment = django.db.models.ForeignKey(Assessment)
    actor = django.db.models.ForeignKey(Actor)
    # Admits blank to enable automatic creation of records
    role = django.db.models.ForeignKey(Role, null=True)
    hazard = django.db.models.ForeignKey(Hazard)


class RiskAssessmentSection(Common):
   """
   Represents Risk Assessment Sections of an assessment
   """
   code = django.db.models.CharField(max_length=5)

class RiskAssessmentQuestionset(Common):
    """
    Represents a Risk Assessment Question Set
    """
    ra_section = django.db.models.ForeignKey(RiskAssessmentSection)
    code = django.db.models.CharField(max_length=10)

class RiskAssessmentQuestion(Common):
   """
   Represents Risk Assessment Questios of an assessment
   """
   ra_questionset = django.db.models.ForeignKey(RiskAssessmentQuestionset)
   code = django.db.models.CharField(max_length=10)
   description = django.db.models.TextField(max_length=200)


class RiskAssessmentQuestionStatement(Common):
   """
   Represents Risk Assessment Question Statements of an assessment
   """
   ra_question = django.db.models.ForeignKey(RiskAssessmentQuestion)
   code = django.db.models.CharField(max_length=15)
   description = django.db.models.TextField(max_length=500)

class AssessmentRAQuestionStatement(Common):
   """
   Represents Risk Assessment Question Statements and values for an assessment
   """
   VALUES = (
      ('L', 'Low'),
      ('M', 'Medium'),
      ('H', 'High'),
   )
   assessment = django.db.models.ForeignKey(Assessment)
   ra_question = django.db.models.ForeignKey(RiskAssessmentQuestion)
   ra_question_statement = django.db.models.ForeignKey(RiskAssessmentQuestionStatement)
   hazard = django.db.models.ForeignKey(Hazard)
   short_term_value = django.db.models.CharField("Short Term",max_length=1,choices=VALUES,null=True,blank=True)
   mid_term_value = django.db.models.CharField("Mid Term",max_length=1,choices=VALUES,null=True,blank=True)
   long_term_value = django.db.models.CharField("Long Term",max_length=1,choices=VALUES,null=True,blank=True)
   mov = django.db.models.CharField("MoV.", max_length=500,null=True,blank=True)
   values_meaning = django.db.models.CharField(max_length=500,null=True,blank=True)

   def get_hazard_name(self):
       try:
           return Hazard.objects.get(pk=self.hazard).name
       except:
           return ""

class AssessmentHazardCausality(Common):
   """
   Represents a record in the causality table between hazards
   """
   VALUES = (
      ('L', 'Low'),
      ('M', 'Medium'),
      ('H', 'High'),
   )
   assessment = django.db.models.ForeignKey(Assessment)
   hazard_occurrence = django.db.models.ForeignKey(Hazard, related_name='hazard_occurrence')
   hazard_impacted = django.db.models.ForeignKey(Hazard, related_name='hazard_impacted')
   short_term_value = django.db.models.CharField(max_length=1,choices=VALUES,null=True, blank=True)
   mid_term_value = django.db.models.CharField(max_length=1,choices=VALUES,null=True, blank=True)
   long_term_value = django.db.models.CharField(max_length=1,choices=VALUES,null=True, blank=True)
   mov = django.db.models.CharField(max_length=500,null=True,blank=True)
   values_meaning = django.db.models.CharField(max_length=500,null=True,blank=True)


class CapacityAssessmentSection(Common):
   """
   Represents Capacity Assessment Sections
   """
   code = django.db.models.CharField(max_length=5)

class CapacityAssessmentSubsection(Common):
    """
    Represents a Capacity Assessment Subsection
    """
    code = django.db.models.CharField(max_length=10)
    ca_section = django.db.models.ForeignKey(CapacityAssessmentSection)

class CapacityAssessmentQuestionSet(Common):
   """
   Represents Capacity Assessment Question set
   """
   code = django.db.models.CharField(max_length=10)
   control_question_code = django.db.models.CharField(max_length=25, blank=True)
   ca_subsection = django.db.models.ForeignKey(CapacityAssessmentSubsection)
   is_block_by_hazard = django.db.models.BooleanField(default=False)

class CapacityAssessmentQuestion(Common):
   """
   Represents Capacity Assessment Question of a Question Set
   """
   code = django.db.models.CharField(max_length=15)
   description = django.db.models.CharField(max_length=500)
   ca_questionset = django.db.models.ForeignKey(CapacityAssessmentQuestionSet)
   is_by_hazard = django.db.models.BooleanField(default=False)


class CapacityAssessmentStatement(Common):
   """
   Represents Capacity Assessment Statement of a Question Set Question
   """
   STATEMENT_TYPES = (
       ('CON','CONTROL'),
       ('YNS','YESNOSIMPLE'),
       ('YNH','YESNOBYHAZARD'),
       ('EFS','EFFECTIVESIMPLE'),
       ('EFH','EFFECTIVEBYHAZARD'),
       ('MFH','MEETINGFREQBYHAZARD'),
       ('MAH','MEETINGATTBYHAZARD'),
   )
   code = django.db.models.CharField(max_length=20)
   ca_question = django.db.models.ForeignKey(CapacityAssessmentQuestion)
   description = django.db.models.TextField(max_length=500)
   weight = django.db.models.DecimalField(decimal_places=3,max_digits=4)
   statement_type = django.db.models.CharField(max_length=1,choices=STATEMENT_TYPES,null=True)
   is_by_hazard = django.db.models.BooleanField(default=False)

class MaxValues(Common):
    """
    List of initial values for any ca statement
    """

class LowMidHighValues(Common):
    """
    List of values for Low/Mid/High options
    """

class YesNoValues(Common):
    """
    Yes No Values
    """

class EffectivenessValues(Common):
    """
    List of effectiveness values
    """

class MeetingFrequencyValues(Common):
    """
    List of meeting frequency values
    """

class MeetingAttendanceValues(Common):
    """
    List of meeting attendance values
    """

class AssessmentCAQuestionStatement(Common):
    """
    Represents a capacity assessment statement
    """
    assessment = django.db.models.ForeignKey(Assessment)
    hazard = django.db.models.ForeignKey(Hazard,blank=True,null=True)
    ca_section = django.db.models.ForeignKey(CapacityAssessmentSection)
    ca_subsection = django.db.models.ForeignKey(CapacityAssessmentSubsection)
    ca_questionset = django.db.models.ForeignKey(CapacityAssessmentQuestionSet)
    ca_question = django.db.models.ForeignKey(CapacityAssessmentQuestion)
    ca_statement = django.db.models.ForeignKey(CapacityAssessmentStatement)
    value = django.db.models.ForeignKey(MaxValues,null=True,
                               blank=True)
    mov = django.db.models.CharField(max_length=250,null=True,blank=True)


