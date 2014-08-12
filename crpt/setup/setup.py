import csv
from django.conf import settings
import datetime

import sys,os
project_path = "/Users/miquel/UN/03-CRPTWeb/crpt/"
sys.path.append(project_path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'crpt.settings'


from crptapp.models import City, Responder, HazardCategory, Hazard, SpatialUnitType, \
    Actor, Role, Assessment, ActorRole, RiskAssessmentSection, RiskAssessmentQuestionStatement, \
    RiskAssessmentQuestion, AssessmentRAQuestionStatement, AssessmentHazardCausality, \
    RiskAssessmentCausalityQuestion, RiskAssessmentCausalityQuestionStatement, AssessmentRACausalityQuestionStatement,\
    CapacityAssessmentSection, CapacityAssessmentSubsection,  \
    CapacityAssessmentQuestionSet, CapacityAssessmentQuestion, CapacityAssessmentStatement,  \
    AssessmentCAYESNOStatement, AssessmentCAEffectivenessStatement, AssessmentCAMeetingAttendanceStatement, \
    AssessmentCAMeetingFrequencyStatement, RiskAssessmentQuestionset


def setup():
    loadfiles()
    create_assessments()
    create_assessments_actor_roles()
    create_assessments_ra_question_statements()
    create_assessments_ra_causality_hazard_matrix()
    create_assessments_ra_causality_question_statements()
    create_assessment_ca_statements()


def loadfiles():
   loadCities(settings.BASE_DIR + "/crpt/files/cities.csv")
   loadResponders(settings.BASE_DIR + "/crpt/files/responders.csv")
   loadHazardCategories(settings.BASE_DIR + "/crpt/files/hazard_categories.csv")
   loadHazards(settings.BASE_DIR + "/crpt/files/hazards.csv")
   loadSpatialUnitTypes(settings.BASE_DIR + "/crpt/files/spatial_unit_types.csv")
   loadActors(settings.BASE_DIR + "/crpt/files/actors.csv")
   loadRoles(settings.BASE_DIR + "/crpt/files/roles.csv")
   loadRASections(settings.BASE_DIR + "/crpt/files/risk_assessment_sections.csv")
   loadRAQuestionStatements(settings.BASE_DIR + "/crpt/files/risk_assessment_questions.csv")
   loadCASections(settings.BASE_DIR + "/crpt/files/capacity_assessment_sections.csv")
   loadCASubsections(settings.BASE_DIR + "/crpt/files/capacity_assessment_subsections.csv")
   load_ca_assessment_questions(settings.BASE_DIR + "/crpt/files/risk_assessment_capacity_questions.csv", False)
   load_ca_assessment_questions(settings.BASE_DIR + "/crpt/files/risk_assessment_capacity_blocks_by_hazard.csv", True)
   load_ca_assessment_questions(settings.BASE_DIR + "/crpt/files/contextual_capacity_questions.csv", False)
   load_ca_assessment_questions(settings.BASE_DIR + "/crpt/files/mitigation_capacity_questions.csv", False)
   load_ca_assessment_questions(settings.BASE_DIR + "/crpt/files/response_and_recovery_capacity_questions.csv", False)
   load_ca_assessment_questions(settings.BASE_DIR + "/crpt/files/response_and_recovery_capacity_blocks_by_hazard.csv", True)
   load_ca_assessment_questions(settings.BASE_DIR + "/crpt/files/monitoring_and_evaluation_capacity_questions.csv", False)

def create_assessment_ca_statements():
    print("create_assessment_ca_statements. Start.")
    for assessment in Assessment.objects.all():
       for ca_section in CapacityAssessmentSection.objects.all():
           for ca_subsection in ca_section.capacityassessmentsubsection_set.all():
              for ca_questionset in ca_subsection.capacityassessmentquestionset_set.all():
                  print"Questionset: " + ca_questionset.code + "- is_block_by_hazard: {}".format(ca_questionset.is_block_by_hazard)
                  if(ca_questionset.is_block_by_hazard==True):
                      # Create block by hazard
                      for hazard in assessment.hazards.all():
                         create_block_by_hazard(assessment, hazard, ca_questionset)
                  else:
                      # Create questions
                      print("ca_questionset: " + ca_questionset.code)
                      for ca_question in ca_questionset.capacityassessmentquestion_set.all():
                          print("ca_question: " + ca_question.code)
                          for ca_statement in ca_question.capacityassessmentstatement_set.all():
                              print("ca_statement: " + ca_statement.code)
                              if(ca_statement.is_by_hazard):
                                  for hazard in assessment.hazards.all():
                                      create_ca_assessment_statement(assessment, ca_statement, hazard)
                              else:
                                create_ca_assessment_statement(assessment, ca_statement, None)

    print("create_assessment_ca_statements. End.")


def create_block_by_hazard(assessment, hazard, ca_questionset):
    print("create_block_by_hazard. Start.")

    for ca_question in ca_questionset.capacityassessmentquestion_set.all():
        for ca_statement in ca_question.capacityassessmentstatement_set.all():
            create_ca_assessment_statement(assessment, ca_statement, hazard)

    print("create_block_by_hazard. End.")


def  create_ca_assessment_statement(assessment, ca_statement, hazard):
    print("create_ca_assessment_statement. Start")
    if(ca_statement.statement_type=='YNS' or ca_statement.statement_type=='YNH'):
       create_ca_assesment_yesno_statement(assessment, ca_statement, hazard)
       pass
    elif(ca_statement.statement_type=='EFH' or ca_statement.statement_type=='EFS'):
       create_ca_assessment_effectiveness_statement(assessment, ca_statement, hazard)
       pass
    elif(ca_statement.statement_type=='MFH' or ca_statement.statement_type=='MFS'):
        create_ca_assessment_meetingfrequency_statement(assessment, ca_statement, hazard)
    elif(ca_statement.statement_type=='MAH' or ca_statement.statement_type=='MAS'):
        create_ca_assessment_meetingattendance_statement(assessment, ca_statement, hazard)
    else:
        print("statement type not found: " + ca_statement.statement_type)

    print("create_ca_assessment_statement. End")

def create_ca_assessment_meetingattendance_statement(assessment, ca_statement, hazard):
    print("create_ca_assessment_meetingattendance_statement. Start")
    assessment_ca_statement = AssessmentCAMeetingAttendanceStatement()
    name = assessment.name
    if(hazard):
        name = name + "-" + hazard.name
    name = name + "-" + ca_statement.code
    print("Creating assessment_ca_statement: " + name)
    assessment_ca_statement.name = name
    assessment_ca_statement.assessment = assessment
    assessment_ca_statement.ca_section = ca_statement.ca_question.ca_questionset.ca_subsection.ca_section
    assessment_ca_statement.ca_subsection = ca_statement.ca_question.ca_questionset.ca_subsection
    assessment_ca_statement.ca_questionset = ca_statement.ca_question.ca_questionset
    assessment_ca_statement.ca_question = ca_statement.ca_question
    assessment_ca_statement.ca_statement = ca_statement
    if(hazard):
        assessment_ca_statement.hazard = hazard
    assessment_ca_statement.save()

    print("create_ca_assessment_meetingattendance_statement. End")

def create_ca_assessment_meetingfrequency_statement(assessment, ca_statement, hazard):
    print("create_ca_assessment_meetingfrequency_statement. Start")
    assessment_ca_statement = AssessmentCAMeetingFrequencyStatement()
    name = assessment.name
    if(hazard):
        name = name + "-" + hazard.name
    name = name + "-" + ca_statement.code
    print("Creating assessment_ca_statement: " + name)
    assessment_ca_statement.name = name
    assessment_ca_statement.assessment = assessment
    assessment_ca_statement.ca_section = ca_statement.ca_question.ca_questionset.ca_subsection.ca_section
    assessment_ca_statement.ca_subsection = ca_statement.ca_question.ca_questionset.ca_subsection
    assessment_ca_statement.ca_questionset = ca_statement.ca_question.ca_questionset
    assessment_ca_statement.ca_question = ca_statement.ca_question
    assessment_ca_statement.ca_statement = ca_statement
    if(hazard):
        assessment_ca_statement.hazard = hazard
    assessment_ca_statement.save()

    print("create_ca_assessment_meetingfrequency_statement. End")

def create_ca_assessment_effectiveness_statement(assessment, ca_statement, hazard):
    print("create_ca_assessment_effectiveness_statement. Start")
    assessment_ca_statement = AssessmentCAEffectivenessStatement()
    name = assessment.name
    if(hazard):
        name = name + "-" + hazard.name
    name = name + "-" + ca_statement.code
    print("Creating assessment_ca_statement: " + name)
    assessment_ca_statement.name = name
    assessment_ca_statement.assessment = assessment
    assessment_ca_statement.ca_section = ca_statement.ca_question.ca_questionset.ca_subsection.ca_section
    assessment_ca_statement.ca_subsection = ca_statement.ca_question.ca_questionset.ca_subsection
    assessment_ca_statement.ca_questionset = ca_statement.ca_question.ca_questionset
    assessment_ca_statement.ca_question = ca_statement.ca_question
    assessment_ca_statement.ca_statement = ca_statement
    if(hazard):
        assessment_ca_statement.hazard = hazard
    assessment_ca_statement.save()

    print("create_ca_assessment_effectiveness_statement. End")

def create_ca_assesment_yesno_statement(assessment, ca_statement, hazard):
    print("create_ca_assesment_yesnosimple. Start")
    assessment_ca_statement = AssessmentCAYESNOStatement()
    name = assessment.name
    if(hazard):
        name = name + "-" + hazard.name
    name = name + "-" + ca_statement.code
    print("Creating assessment_ca_statement: " + name)
    assessment_ca_statement.name = name
    assessment_ca_statement.assessment = assessment
    assessment_ca_statement.ca_section = ca_statement.ca_question.ca_questionset.ca_subsection.ca_section
    assessment_ca_statement.ca_subsection = ca_statement.ca_question.ca_questionset.ca_subsection
    assessment_ca_statement.ca_questionset = ca_statement.ca_question.ca_questionset
    assessment_ca_statement.ca_question = ca_statement.ca_question
    assessment_ca_statement.ca_statement = ca_statement
    if(hazard):
        assessment_ca_statement.hazard = hazard
    assessment_ca_statement.save()

    print("create_ca_assesment_yesnosimple. End")


def create_assessments_ra_causality_hazard_matrix():
   print("Create Causality Hazard Matrix for Assessments. Start")
   for assessment in Assessment.objects.all():
      for hazard_occurrence in assessment.hazards.all():
         for hazard_impacted in assessment.hazards.all():
             if(hazard_occurrence.name.strip() <> hazard_impacted.name.strip()):
                 assessment_hazard_causality = AssessmentHazardCausality()
                 assessment_hazard_causality.hazard_impacted = hazard_impacted
                 assessment_hazard_causality.hazard_occurrence = hazard_occurrence
                 assessment_hazard_causality.name = assessment.name + "-" + hazard_occurrence.name + "-" + hazard_impacted.name
                 assessment_hazard_causality.assessment = assessment
                 print("Creating hazard causality: " + assessment_hazard_causality.name)
                 assessment_hazard_causality.save()

   print("Create Causality Hazard Matrix for Assessments. End")

def create_assessments_ra_causality_question_statements():
    print("Create RACausalityQuestionStatments for Assessments. Start.")
    for assessment in Assessment.objects.all():
        for hazard in assessment.hazards.all():
           for ra_causality_question_statement in RiskAssessmentCausalityQuestionStatement.objects.all():
              assessment_ra_causality_question_statement = AssessmentRACausalityQuestionStatement()
              assessment_ra_causality_question_statement.name = assessment.name + "-" + ra_causality_question_statement.name + "-" + hazard.name
              assessment_ra_causality_question_statement.assessment = assessment
              assessment_ra_causality_question_statement.hazard = hazard
              assessment_ra_causality_question_statement.ra_section = ra_causality_question_statement.ra_section
              assessment_ra_causality_question_statement.ra_causality_question = ra_causality_question_statement.ra_causality_question
              assessment_ra_causality_question_statement.ra_causality_question_statement = ra_causality_question_statement
              assessment_ra_causality_question_statement.save()

    print("Create RACausalityQuestionStatments for Assessments. End.")

def create_assessments_ra_question_statements():
    print("Create RAQuestionStatments for Assessments. Start")
    for assessment in Assessment.objects.all():
        for hazard in assessment.hazards.all():
            for ra_question_statement in RiskAssessmentQuestionStatement.objects.all():
                 assessment_ra_question_statement = AssessmentRAQuestionStatement()
                 assessment_ra_question_statement.name = assessment.name + "-" + ra_question_statement.code + "-" + hazard.name
                 print("Creating asessment_question_statement:" + assessment_ra_question_statement.name)
                 assessment_ra_question_statement.assessment = assessment
                 assessment_ra_question_statement.hazard = hazard
                 assessment_ra_question_statement.ra_question_statement = ra_question_statement
                 assessment_ra_question_statement.ra_question = ra_question_statement.ra_question
                 assessment_ra_question_statement.save()

    print("Create RAQuestionStatments for Assessments. End")

def create_assessments_actor_roles():
    print("Create Actor Roles. Start")

    for assessment in Assessment.objects.all():
        for actor in assessment.actors.all():
            for hazard in assessment.hazards.all():
                actor_role = ActorRole()
                actor_role.name = assessment.name + "-" + actor.name + "-" + hazard.name
                print("Creating actor role: " + actor_role.name)
                actor_role.assessment = assessment
                actor_role.actor = actor
                actor_role.hazard = hazard
                actor_role.save()

    print("Create Actor Roles. End")

def create_assessments():
   print("Create Assessment. Start")

   assessment = Assessment()
   assessment.name = "Assessment 1"
   assessment.initial_date = datetime.datetime.now()
   assessment.spatial_unit_type = SpatialUnitType.objects.get(id=1)
   assessment.city = City.objects.get(id=1)
   assessment.save()
   assessment.actors = Actor.objects.all()
   assessment.hazards = Hazard.objects.all()
   assessment.save()

   print("Create Assessment. End")


def load_ca_assessment_questions(file_path, is_block_by_hazard):
    print("load_ca_assessment_questions. {} is_block_by_hazard: {} .Start.".format(file_path,is_block_by_hazard))
    dataReader = csv.reader(open(file_path), delimiter=',', quotechar='"')
    for row in dataReader:
       ca_statement = CapacityAssessmentStatement()
       ca_statement.code = row[4].strip()
       ca_statement.name = ca_statement.code
       print("Loading CapacityAssessmentStatement: " + ca_statement.code + ". subsection: " + row[1].strip())
       ca_subsection = CapacityAssessmentSubsection.objects.get(code=row[1].strip())
       try:
           ca_questionset = CapacityAssessmentQuestionSet.objects.get(code=row[2].strip())
       except:
           ca_questionset = CapacityAssessmentQuestionSet()
           ca_questionset.code = row[2].strip()
           ca_questionset.name = ca_questionset.code
           ca_questionset.ca_subsection = ca_subsection
           ca_questionset.is_block_by_hazard = is_block_by_hazard
           print("Saving questionset: " + ca_questionset.code + ". is_block_by_hazard: {}".format(ca_questionset.is_block_by_hazard) )
           ca_questionset.save()
       try:
          ca_question = CapacityAssessmentQuestion.objects.get(code=row[3].strip())
       except:
          ca_question = CapacityAssessmentQuestion()
          ca_question.code = row[3].strip()
          ca_question.name = ca_question.code
          ca_question.ca_questionset = ca_questionset
          print("Saving question: " + ca_question.code)
          ca_question.save()
       if(is_block_by_hazard==False and 'H' in row[5].strip()):
           ca_statement.is_by_hazard = True
       ca_statement.ca_question = ca_question
       ca_statement.statement_type = row[5].strip()
       print("Description: " + row[6].strip())
       ca_statement.description = row[6].strip()
       print("Weight: " + row[7].strip())
       ca_statement.weight = row[7].strip()
       ca_statement.save()

    print("load_ca_assessment_questions. End.")


def loadCASections(file_path):
   print("Loading CASections: " + file_path + ". Start.")
   dataReader = csv.reader(open(file_path), delimiter=',', quotechar='"')
   for row in dataReader:
       print("Loading CASection: "+ row[0])
       ca_section = CapacityAssessmentSection()
       ca_section.code = row[0].strip()
       ca_section.name = row[1].strip()
       ca_section.save()
   print("")
   print("Loading CASections: " + file_path + ". End.")

def loadCASubsections(file_path):
   print("Loading CASubsections: " + file_path + ". Start.")
   dataReader = csv.reader(open(file_path), delimiter=',', quotechar='"')
   for row in dataReader:
       print("Loading CASubsection: "+ row[1])
       ca_section = CapacityAssessmentSection.objects.get(code=row[0].strip())
       ca_subsection = CapacityAssessmentSubsection()
       ca_subsection.code = row[1].strip()
       ca_subsection.name = row[2].strip()
       ca_subsection.ca_section = ca_section
       ca_subsection.save()
   print("")
   print("Loading CASubsections: " + file_path + ". End.")



def loadRACausalityQuestionStatements(file_path):
   print("Loading RACausalityQuestionStatements: " + file_path + ". Start.")
   print("")
   dataReader = csv.reader(open(file_path), delimiter=',', quotechar='"')
   for row in dataReader:
      print("Loading RACausalityQuestionStatements: "+ row[2])
      try:
         ra_section = RiskAssessmentSection.objects.get(code=row[0].strip())
      except:
         ra_section = RiskAssessmentSection()
         ra_section.name = row[0].strip()
         ra_section.code = ra_section.name
         ra_section.save()
      try:
         ra_causality_question =  RiskAssessmentQuestion.objects.get(code=row[1].strip())
      except:
         ra_causality_question = RiskAssessmentCausalityQuestion()
         ra_causality_question.code = row[1].strip()
         ra_causality_question.name = ra_section.code + "-" + ra_causality_question.code
         ra_causality_question.save()
      ra_causality_question_statement = RiskAssessmentCausalityQuestionStatement()
      ra_causality_question_statement.question_code = row[1].strip()
      ra_causality_question_statement.code = row[2].strip()
      ra_causality_question_statement.name = ra_causality_question_statement.code
      ra_causality_question_statement.description = row[3].strip()
      ra_causality_question_statement.ra_causality_question = ra_causality_question
      ra_causality_question_statement.ra_section = ra_section
      ra_causality_question_statement.save()
   print("")
   print("Loading RACausalityQuestionStatements: " + file_path + ". End.")

def loadRAQuestionStatements(file_path):
   print("Loading RAQuestionStatements: " + file_path + ". Start.")
   print("")
   dataReader = csv.reader(open(file_path), delimiter=',', quotechar='"')
   for row in dataReader:
      print("Loading RAQuestionStatement: "+ row[3])
      rasection = RiskAssessmentSection.objects.get(code=row[0].strip())
      try:
          raquestionset = RiskAssessmentQuestionset.objects.get(code=row[1].strip())
      except:
          raquestionset = RiskAssessmentQuestionset()
          raquestionset.ra_section = rasection
          raquestionset.name = row[1].strip()
          raquestionset.code = raquestionset.name
          raquestionset.save()
      try:
         raquestion =  RiskAssessmentQuestion.objects.get(code=row[2].strip())
      except:
         raquestion = RiskAssessmentQuestion()
         raquestion.ra_questionset = raquestionset
         raquestion.code = row[2].strip()
         raquestion.name = rasection.code + "-" + raquestion.code
         raquestion.description = row[4].strip();
         raquestion.save()
      raquestionStatement = RiskAssessmentQuestionStatement()
      raquestionStatement.question_code = row[2].strip()
      raquestionStatement.code = row[3].strip()
      raquestionStatement.name = raquestionStatement.code
      raquestionStatement.description = row[4].strip()
      raquestionStatement.ra_question = raquestion
      raquestionStatement.save()
   print("")
   print("Loading RAQuestionStatements: " + file_path + ". End.")



def loadRASections(file_path):
   print("Loading RASections: " + file_path + ". Start.")
   dataReader = csv.reader(open(file_path), delimiter=',', quotechar='"')
   for row in dataReader:
       print("Loading RASection: "+ row[0])
       rasection = RiskAssessmentSection()
       print("Loading RASection: " + row[0])
       rasection.code = row[0].strip()
       rasection.name = row[1].strip()
       rasection.save()
   print("")
   print("Loading RASections: " + file_path + ". End.")


def loadActors(file_path):
   print("Loading actors: " + file_path + ". Start.")
   dataReader = csv.reader(open(file_path), delimiter=',', quotechar='"')
   for row in dataReader:
       print("Loading actor: "+ row[0])
       actor = Actor()
       print("Loading actors: " + row[0] + ". Start.")
       actor.name = row[0].strip()
       actor.save()
   print("")
   print("Loading actors: " + file_path + ". End.")

def loadRoles(file_path):
   print("Loading roles: " + file_path + ". Start.")
   print("")
   dataReader = csv.reader(open(file_path), delimiter=',', quotechar='"')
   for row in dataReader:
      print("Loading role: "+ row[0])
      role = Role()
      role.name = row[0].strip()
      role.save()
   print("")
   print("Loading roles: " + file_path + ". End.")

def loadCities(file_path):
   print("Loading cities: " + file_path + ". Start.")
   print("")
   dataReader = csv.reader(open(file_path), delimiter=',', quotechar='"')
   for row in dataReader:
      print("Loading City: "+ row[0])
      city = City()
      city.name = row[0].strip()
      city.save()
   print("")
   print("Loading cities: " + file_path + ". End.")

def loadResponders(file_path):
   print("Loading responders: " + file_path + ". Start.")
   print("")
   dataReader = csv.reader(open(file_path), delimiter=',', quotechar='"')
   for row in dataReader:
      print("Loading responder: "+ row[0])
      responder = Responder()
      responder.name = row[0].strip()
      responder.organization =  row[1].strip()
      responder.position = row[2].strip()
      responder.email = row[3].strip()
      responder.save()
   print("")
   print("Loading responders: " + file_path + ". End.")

def loadHazardCategories(file_path):
   print("Loading Hazard Categories: " + file_path + ". Start.")
   print("")
   dataReader = csv.reader(open(file_path), delimiter=',', quotechar='"')
   for row in dataReader:
      print("Loading category: "+ row[0])
      category = HazardCategory()
      category.name = row[0].strip()
      category.save()
   print("")
   print("Loading Hazard Categories: " + file_path + ". End.")

def loadHazards(file_path):
   print("Loading Hazards: " + file_path + ". Start.")
   print("")
   dataReader = csv.reader(open(file_path), delimiter=',', quotechar='"')
   for row in dataReader:
      print("Loading hazard: "+ row[0] + ". Category: " + row[1])
      hazard = Hazard()
      hazard.name = row[0].strip()
      print(hazard.name)
      hazard.category = HazardCategory.objects.get(name=row[1].strip())
      hazard.save()
   print("")
   print("Loading Hazards: " + file_path + ". End.")

def loadSpatialUnitTypes(file_path):
   print("Loading spus: " + file_path + ". Start.")
   print("")
   dataReader = csv.reader(open(file_path), delimiter=',', quotechar='"')
   for row in dataReader:
      print("Loading spu: " + row[0])
      spu = SpatialUnitType()
      spu.name = row[0].strip()
      spu.save()
   print("")
   print("Loading spus: " + file_path + ". End.")

if __name__ == "__main__":
   setup()

