from django.conf.urls import patterns, url

import views

urlpatterns = patterns('',
    # List of assessment for current user (city)
    url(r'^$', views.assessmentIndex, name='index'),
    # Edit form for assessments
    url(r'^(?P<assessment_id>\d+)/(?P<assessment_name>[^/]+)/$', views.getAssessmentForm , name='assessment_detail'),
    # List of Capacity Assessment Questions
    url(r'^capacity_assessment/(?P<ca_section_id>\d+)/(?P<ca_subsection_id>\d+)/(?P<assessment_id>\d+)/$', views.getCASubsectionQuestions , name='ca_subsection_questions'),
    # List of Risk Assessment Questions
    url(r'^risk_assessment/(?P<ra_section_id>\d+)/(?P<assessment_id>\d+)/$', views.getRASectionQuestionsPaginated , name='ra_section_questions'),
    # Statements of a Risk Assessment Question (question detail)
    url(r'^risk_assessment/(?P<ra_question_id>\d+)/(?P<ra_section_id>\d+)/(?P<assessment_id>\d+)/$', views.getRAQuestionStatements , name='ra_section_question_statements'),
    # Formset of causality matrix
    url(r'^risk_assessment/causality/(?P<assessment_id>\d+)/(?P<ra_question_id>\d+)/$', views.getCausalityMatrixQuestions , name='ra_causality_matrix_questions'),
    # Capacity Assessment GenericStatement detail form
    url(r'^(?P<statement_id>\d+)/$', views.getCAGenericStatementForm , name='ca_generic_statement_detail'),
    # Capacity Assessment Question Statements by assessment and hazard
    url(r'^capacity_assessment/capacity_questions/(?P<assessment_id>\d+)/(?P<hazard_id>\d+)/(?P<ca_subsection_id>\d+)/$', views.getCASubsectionQuestionsByHazard, name='ca_statement_detail_by_hazard'),
    # Capacity Assessment Question Statements by assessment and question
    url(r'^capacity_assessment/(?P<assessment_id>\d+)/(?P<question_id>\d+)/$', views.getCAStatementByAssessmentQuestion, name='ca_statement_detail_by_question'),
    # Assessment  Statement detail
    url(r'^capacity_assessment/(?P<statement_id>\d+)/$', views.getCAStatement, name='ca_statement_detail_by_id'),



    # To get widgets from admin running OK!!
    (r'^admin/jsi18n/', 'django.views.i18n.javascript_catalog'),
)