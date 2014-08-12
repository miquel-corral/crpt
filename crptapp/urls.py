from django.conf.urls import patterns, url

import views

urlpatterns = patterns('',
    # Implementation using generic views
    #url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^$', views.assessmentIndex, name='index'),
    url(r'^(?P<assessment_id>\d+)/(?P<assessment_name>[^/]+)/$', views.getAssessmentForm , name='assessment_detail'),
    #url(r'^risk_assessment/(?P<ra_section_id>\d+)/(?P<assessment_id>\d+)/$', views.getRASectionQuestions , name='ra_section_questions'),
    url(r'^capacity_assessment/(?P<ca_section_id>\d+)/(?P<ca_subsection_id>\d+)/(?P<assessment_id>\d+)/$', views.getCASubsectionQuestions , name='ca_subsection_questions'),
    url(r'^risk_assessment/(?P<ra_section_id>\d+)/(?P<assessment_id>\d+)/$', views.getRASectionQuestionsPaginated , name='ra_section_questions'),

    url(r'^risk_assessment/(?P<ra_question_id>\d+)/(?P<ra_section_id>\d+)/(?P<assessment_id>\d+)/$', views.getRAQuestionStatements , name='ra_section_question_statements'),

    url(r'^(?P<statement_id>\d+)/$', views.getCAGenericStatementForm , name='ca_generic_statement_detail'),

    (r'^admin/jsi18n/', 'django.views.i18n.javascript_catalog'),
)