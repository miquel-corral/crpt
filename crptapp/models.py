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

    """
    Relationships:
        many to many with Assessment ??
        many to many with City >> set in City
    """

class HazardCategory(Common):
    """
    Represents a Hazard Category
    """

class Hazard(Common):
    """
    Represents a single Hazard:

    """

    """
       Relationships
          one to many with HazardCategory
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

    """
    Relationships
        many to many with Responder just in case a Responder could assess more than one city
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

    """
    Relationships:
        one to one with City
        many to many with Hazard
        one to many with Spatial Unit Type
        many to many with Actor
    """
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
   mov = django.db.models.TextField("MoV.", max_length=250,null=True,blank=True)
   values_meaning = django.db.models.TextField(max_length=250,null=True,blank=True)

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
   mov = django.db.models.TextField(max_length=250,null=True,blank=True)
   values_meaning = django.db.models.TextField(max_length=250,null=True,blank=True)

"""
class RiskAssessmentCausalityQuestion(Common):
   ""
   Represents Risk Assessment Causality Questions of an assessment
   ""
   code = django.db.models.CharField(max_length=10)

class RiskAssessmentCausalityQuestionStatement(Common):
   ""
   Represents Risk Assessment Causality Question Statements of an assessment
   ""
   ra_section = django.db.models.ForeignKey(RiskAssessmentSection)
   ra_causality_question = django.db.models.ForeignKey(RiskAssessmentCausalityQuestion)
   code = django.db.models.CharField(max_length=15)
   description = django.db.models.TextField(max_length=500)

class AssessmentRACausalityQuestionStatement(Common):
   ""
   Represents a causality question statement for an assessment
   ""
   VALUES = (
      ('L', 'Low'),
      ('M', 'Medium'),
      ('H', 'High'),
   )
   assessment = django.db.models.ForeignKey(Assessment)
   hazard = django.db.models.ForeignKey(Hazard)
   ra_section = django.db.models.ForeignKey(RiskAssessmentSection)
   ra_causality_question = django.db.models.ForeignKey(RiskAssessmentCausalityQuestion)
   ra_causality_question_statement = django.db.models.ForeignKey(RiskAssessmentCausalityQuestionStatement)
   value = django.db.models.CharField(max_length=1,choices=VALUES,null=True)
   mov = django.db.models.TextField(max_length=250,null=True,blank=True)
   values_meaning = django.db.models.TextField(max_length=250,null=True,blank=True)
"""

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
   control_question_code = django.db.models.TextField(max_length=25, blank=True)
   ca_subsection = django.db.models.ForeignKey(CapacityAssessmentSubsection)
   is_block_by_hazard = django.db.models.BooleanField(default=False)

class CapacityAssessmentQuestion(Common):
   """
   Represents Capacity Assessment Question of a Question Set
   """
   code = django.db.models.CharField(max_length=15)
   description = django.db.models.TextField(max_length=500)
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

class ValueListType():
    value_class = django.db.TextField(max_lengt=10)

class AssessmentCAQuestionStatement(Common):
    """

    """
    VALUES = (
      ('Y', 'Yes'),
      ('N', 'No'),
    )
    assessment = django.db.models.ForeignKey(Assessment)
    hazard = django.db.models.ForeignKey(Hazard,blank=True,null=True)
    ca_section = django.db.models.ForeignKey(CapacityAssessmentSection)
    ca_subsection = django.db.models.ForeignKey(CapacityAssessmentSubsection)
    ca_questionset = django.db.models.ForeignKey(CapacityAssessmentQuestionSet)
    ca_question = django.db.models.ForeignKey(CapacityAssessmentQuestion)
    ca_statement = django.db.models.ForeignKey(CapacityAssessmentStatement)
    value = django.db.models.CharField(max_length=1,choices=VALUES,null=True,blank=True)
    mov = django.db.models.TextField(max_length=250,null=True,blank=True)
    value_list_type = django.db.models.ForeignKey(ValueListType)

"""
class AssessmentCAYESNOStatement(Common):

    VALUES = (
      ('Y', 'Yes'),
      ('N', 'No'),
    )
    assessment = django.db.models.ForeignKey(Assessment)
    hazard = django.db.models.ForeignKey(Hazard,blank=True,null=True)
    ca_section = django.db.models.ForeignKey(CapacityAssessmentSection)
    ca_subsection = django.db.models.ForeignKey(CapacityAssessmentSubsection)
    ca_questionset = django.db.models.ForeignKey(CapacityAssessmentQuestionSet)
    ca_question = django.db.models.ForeignKey(CapacityAssessmentQuestion)
    ca_statement = django.db.models.ForeignKey(CapacityAssessmentStatement)
    value = django.db.models.CharField(max_length=1,choices=VALUES,null=True)
    mov = django.db.models.TextField(max_length=250,null=True,blank=True)

class AssessmentCAEffectivenessStatement(Common):
    VALUES = (
      ('100%', '100%'),
      ('75-99%', '75-99%'),
      ('50-74%', '50-74%'),
      ('25-49%', '25-49%'),
      ('1-24%', '1-24%'),
      ('0%', '0% or not effective'),
    )
    assessment = django.db.models.ForeignKey(Assessment)
    hazard = django.db.models.ForeignKey(Hazard,blank=True,null=True)
    ca_section = django.db.models.ForeignKey(CapacityAssessmentSection)
    ca_subsection = django.db.models.ForeignKey(CapacityAssessmentSubsection)
    ca_questionset = django.db.models.ForeignKey(CapacityAssessmentQuestionSet)
    ca_question = django.db.models.ForeignKey(CapacityAssessmentQuestion)
    ca_statement = django.db.models.ForeignKey(CapacityAssessmentStatement)
    value = django.db.models.CharField(max_length=7,choices=VALUES,null=True)
    mov = django.db.models.TextField(max_length=250,null=True,blank=True)

class AssessmentCAMeetingFrequencyStatement(Common):
    VALUES = (
      ('0', 'No meetings'),
      ('1', 'Ad Hoc'),
      ('2', 'Annual'),
      ('3', 'one meeting every six months'),
      ('4', 'one meeting per quarter'),
      ('5', 'one meeting per month'),
    )
    assessment = django.db.models.ForeignKey(Assessment)
    hazard = django.db.models.ForeignKey(Hazard,blank=True,null=True)
    ca_section = django.db.models.ForeignKey(CapacityAssessmentSection)
    ca_subsection = django.db.models.ForeignKey(CapacityAssessmentSubsection)
    ca_questionset = django.db.models.ForeignKey(CapacityAssessmentQuestionSet)
    ca_question = django.db.models.ForeignKey(CapacityAssessmentQuestion)
    ca_statement = django.db.models.ForeignKey(CapacityAssessmentStatement)
    value = django.db.models.CharField(max_length=1,choices=VALUES,null=True)
    mov = django.db.models.TextField(max_length=250,null=True,blank=True)

class AssessmentCAMeetingAttendanceStatement(Common):

    VALUES = (
      ('100%', '100% of formal role-holders in regular attendance'),
      ('75%', '75% of formal role-holders in regular attendance'),
      ('50%', '50% of formal role-holders in regular attendance'),
      ('<50%', 'less than 50% of neighborhoods'),
    )

    assessment = django.db.models.ForeignKey(Assessment)
    hazard = django.db.models.ForeignKey(Hazard,blank=True,null=True)
    ca_section = django.db.models.ForeignKey(CapacityAssessmentSection)
    ca_subsection = django.db.models.ForeignKey(CapacityAssessmentSubsection)
    ca_questionset = django.db.models.ForeignKey(CapacityAssessmentQuestionSet)
    ca_question = django.db.models.ForeignKey(CapacityAssessmentQuestion)
    ca_statement = django.db.models.ForeignKey(CapacityAssessmentStatement)
    value = django.db.models.CharField(max_length=5,choices=VALUES,null=True)
    mov = django.db.models.TextField(max_length=250,null=True,blank=True)

class AssessmentCAGenericStatement(Common):

    YESNO = (
      ('Y', 'Yes'),
      ('N', 'No'),
    )
    EFFECTIVENESS = (
      ('100%', '100%'),
      ('75-99%', '75-99%'),
      ('50-74%', '50-74%'),
      ('25-49%', '25-49%'),
      ('1-24%', '1-24%'),
      ('0%', '0% or not effective'),
    )
    MEETING_FREQUENCY = (
      ('0', 'No meetings'),
      ('1', 'Ad Hoc'),
      ('2', 'Annual'),
      ('3', 'one meeting every six months'),
      ('4', 'one meeting per quarter'),
      ('5', 'one meeting per month'),
    )
    MEETING_ATENDANCE = (
      ('100%', '100% of formal role-holders in regular attendance'),
      ('75%', '75% of formal role-holders in regular attendance'),
      ('50%', '50% of formal role-holders in regular attendance'),
      ('<50%', 'less than 50% of neighborhoods'),
    )


    VALUES = (
        ('1','1'),
        ('2','2'),
        ('3','3'),
        ('4','4'),
        ('5','5'),
        ('6','6'),
        ('7','7'),
        ('8','8'),
        ('9','9'),
        ('10','10'),
    )

    assessment = django.db.models.ForeignKey(Assessment)
    hazard = django.db.models.ForeignKey(Hazard,blank=True,null=True)
    ca_section = django.db.models.ForeignKey(CapacityAssessmentSection)
    ca_subsection = django.db.models.ForeignKey(CapacityAssessmentSubsection)
    ca_questionset = django.db.models.ForeignKey(CapacityAssessmentQuestionSet)
    ca_question = django.db.models.ForeignKey(CapacityAssessmentQuestion)
    ca_statement = django.db.models.ForeignKey(CapacityAssessmentStatement)
    value = django.db.models.CharField(max_length=2,choices=VALUES,null=True)
    mov = django.db.models.TextField(max_length=250,null=True,blank=True)
"""