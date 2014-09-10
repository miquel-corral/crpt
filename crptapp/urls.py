from django.conf.urls import patterns, url
import views
from django.contrib.auth import views as auth_views

urlpatterns = patterns('',
    # List of assessments for current user (city) --> assessments.html
    url(r'^$', views.assessment_index, name='index'),
    # Edit form for assessments --> assessment_detail.html
    url(r'^(?P<assessment_id>\d+)/(?P<assessment_name>[^/]+)/$', views.get_assessment_form , name='assessment_detail'),

    # List of Risk Assessment Questions --> ra_questions.html
    url(r'^risk_assessment/(?P<ra_section_id>\d+)/(?P<assessment_id>\d+)/$', views.get_ra_section_questions , name='ra_section_questions'),
    # Statements of a Risk Assessment Question (question detail) --> question_detail.html
    url(r'^risk_assessment/(?P<ra_question_id>\d+)/(?P<ra_section_id>\d+)/(?P<assessment_id>\d+)/$', views.get_ra_question_statements , name='ra_section_question_statements'),
    # Formset of causality matrix --> ra_causality_question_detail.html
    url(r'^risk_assessment/causality/(?P<assessment_id>\d+)/(?P<ra_question_id>\d+)/$', views.get_causality_matrix_questions , name='ra_causality_matrix_questions'),

    # List of Capacity Assessment Questions --> ca_questions.html
    url(r'^capacity_assessment/(?P<ca_section_id>\d+)/(?P<ca_subsection_id>\d+)/(?P<assessment_id>\d+)/$', views.get_ca_subsection_questions , name='ca_subsection_questions'),
    # Capacity Assessment GenericStatement detail form -->
    url(r'^(?P<statement_id>\d+)/$', views.get_ca_generic_statement_form , name='ca_generic_statement_detail'),
    # Capacity Assessment Question Statements by assessment and hazard -->
    url(r'^capacity_assessment/capacity_questions/(?P<assessment_id>\d+)/(?P<hazard_id>\d+)/(?P<ca_subsection_id>\d+)/$', views.get_ca_subsection_questions_by_hazard, name='ca_statement_detail_by_hazard'),
    # Capacity Assessment Question Statements by assessment and question
    url(r'^capacity_assessment/(?P<assessment_id>\d+)/(?P<question_id>\d+)/$', views.get_ca_statement_by_assessment_question, name='ca_statement_detail_by_question'),
    # Assessment  Statement detail
    url(r'^capacity_assessment/hazard_question/(?P<assessment_id>\d+)/(?P<hazard_id>\d+)/(?P<statement_id>\d+)/$', views.get_ca_statement, name='ca_statement_detail_by_id'),


    # Necessary to get widgets from admin running OK
    (r'^admin/jsi18n/', 'django.views.i18n.javascript_catalog'),

)