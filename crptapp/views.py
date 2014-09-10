# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.template import RequestContext, loader
from models import Assessment, RiskAssessmentSection, \
    CapacityAssessmentSection, AssessmentRAQuestionStatement, \
    Actor, RiskAssessmentQuestion, Hazard, \
    RiskAssessmentQuestionset, AssessmentHazardCausality, \
    CapacityAssessmentQuestionSet, CapacityAssessmentQuestion, \
    AssessmentCAQuestionStatement, CapacityAssessmentSubsection, \
    MeetingAttendanceValues, MeetingFrequencyValues, \
    EffectivenessValues, YesNoValues
from django.shortcuts import render_to_response
from django.forms.models import modelformset_factory
from django import forms
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
import logging

from crptapp.settings import *

logger = logging.getLogger(__name__)

@ensure_csrf_cookie
@login_required
def get_assessment_form(request, assessment_id=None, assessment_name=None):
    """
    View for creating/editing an assessment

    :param request:
    :param assessment_id:
    :param assessment_name:
    :return:
    """
    AssessmentFormSet = modelformset_factory(Assessment,max_num=1,
         widgets={'initial_date': \
                      forms.TextInput(attrs={'class':'vDateField'}),
                  'final_date': forms.TextInput(attrs={'class':'vDateField'}),
                  'last_update': forms.HiddenInput()
                  })
    num_errors = 0
    if request.method == 'POST':
        formset = AssessmentFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            return render_to_response("crptapp/assessments.html",
                                {'assessment_list':Assessment.objects.all()})
        else:
            if format(len(formset.errors) > 0):
                num_errors = len(formset.errors[0])
    else:
        query_set = Assessment.objects.filter(pk=assessment_id)
        formset = AssessmentFormSet(queryset = query_set)
    return render_to_response("crptapp/assessment_detail.html", {
        "formset": formset,
        "num_errors":num_errors,
        "assessment_name":assessment_name},
        context_instance=RequestContext(request))

@login_required
def assessment_index(request):
    """
    View for the assessment list
    TODO: filter by user/city

    :param request:
    :return:
    """

    assessments = Assessment.objects.all()
    ra_sections = RiskAssessmentSection.objects.all()
    ca_sections = CapacityAssessmentSection.objects.all()
    template = loader.get_template('crptapp/assessments.html')
    context = RequestContext(request, {
        'assessments': assessments,
        'ra_sections': ra_sections,
        'ca_sections': ca_sections,
    })
    return HttpResponse(template.render(context))

@login_required
def get_ca_subsection_questions(request, ca_section_id, ca_subsection_id,
                                assessment_id):
    """
    View for the ca subsection questions
    :param request:
    :param ra_section_id:
    :param assessment_id:
    :return:
    """

    # only questions not hazard-related

    assessment = Assessment.objects.get(pk=assessment_id)

    ca_section = CapacityAssessmentSection.objects.get(pk=ca_section_id)
    ca_subsection = CapacityAssessmentSubsection.objects.get(pk=ca_subsection_id)
    ca_question_list = []
    num_hazard_related_questions = 0
    ca_questionset_list = \
        CapacityAssessmentQuestionSet.objects.filter(ca_subsection_id=
                                                     ca_subsection_id).\
            order_by('ca_subsection','code')
    print("Questionsetlist Len: " + format(len(ca_questionset_list)))
    for ca_questionset in ca_questionset_list:
        # exclusion in filter is_by_hazard
        ca_question_list.extend(
            CapacityAssessmentQuestion.objects.filter(ca_questionset=
                                                      ca_questionset,
                                                      is_by_hazard=False).
            order_by('ca_questionset','code'))
        # check if any question hazard-related
        num_hazard_related_questions += \
            CapacityAssessmentQuestion.objects.filter(ca_questionset=
                                                      ca_questionset,
                                                      is_by_hazard=True).\
                count()

    paginator = Paginator(ca_question_list, 25) # Show 25 items per page
    page = request.GET.get('page')
    try:
        questions = paginator.page(page)
    except:
        questions = paginator.page(1)
    return render_to_response('crptapp/ca_questions.html',
        {"questions": questions,\
        "assessment":assessment, \
        "num_hazard_related_questions":num_hazard_related_questions,\
        "ca_subsection":ca_subsection,\
        "ca_section":ca_section})

@login_required
def get_ca_subsection_questions_by_hazard(request, assessment_id,
                                          ca_subsection_id, hazard_id):
    """
    View for ca subsection questions block by hazard
    :param request:
    :param assessment_id:
    :param ca_subsection_id:
    :param hazard_id:
    :return:
    """
    assessment = Assessment.objects.get(pk=assessment_id)
    ca_subsection = CapacityAssessmentSubsection.objects.get(pk=
                                                             ca_subsection_id)
    ca_section = ca_subsection.ca_section
    hazard = Hazard.objects.get(pk=hazard_id)
    # selection of question statements, no questions, to show each description
    ca_question_list = AssessmentCAQuestionStatement.objects.filter(
        assessment=assessment_id,
        ca_subsection=ca_subsection_id,
        hazard=hazard_id).order_by('ca_subsection', 'ca_question', 'id')

    paginator = Paginator(ca_question_list, 25) # Show 25 items per page
    page = request.GET.get('page')
    try:
        questions = paginator.page(page)
    except:
        questions = paginator.page(1)
    return render_to_response('crptapp/ca_questions_by_hazard.html', {
        "questions": questions,
        "assessment":assessment,
        "ca_section":ca_section,
        "ca_subsection":ca_subsection,
        "hazard":hazard})

@login_required
def get_ra_section_questions(request, ra_section_id, assessment_id):
    """
    View for ra section questions
    :param request:
    :param ra_section_id:
    :param assessment_id:
    :return:
    """
    assessment = Assessment.objects.get(pk=assessment_id)
    ra_section = RiskAssessmentSection.objects.get(pk=ra_section_id)
    ra_questionset_list = \
        RiskAssessmentQuestionset.objects.filter(ra_section=ra_section_id)
    question_list = \
        RiskAssessmentQuestion.objects.filter(ra_questionset=
                                              ra_questionset_list).\
            order_by('id')
    paginator = Paginator(question_list, 25) # Show 25 items per page
    page = request.GET.get('page')
    try:
        questions = paginator.page(page)
    except:
        questions = paginator.page(1)
    return render_to_response('crptapp/ra_questions.html',
                              {"questions": questions,
                               "assessment":assessment,
                               "ra_section":ra_section,})

@ensure_csrf_cookie
@login_required
def get_ca_generic_statement_form(request, statement_id):
    """
    View for generic statement form
    :param request:
    :param statement_id:
    :return:
    """
    CAGenericStatmentFormSet = \
        modelformset_factory(AssessmentCAQuestionStatement,max_num=1)

    if request.method == 'POST':
        formset = CAGenericStatmentFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            return render_to_response("crptapp/assessments.html",
                                      {'assessment_list':
                                           Assessment.objects.all()})
        else:
            if format(len(formset.errors) > 0):
                num_errors = len(formset.errors[0])
            formset.forms[0].fields['value'] = \
                forms.ModelChoiceField(queryset=Actor.objects.all())
    else:
        query_set = \
            AssessmentCAQuestionStatement.objects.filter(pk=statement_id)
        formset = CAGenericStatmentFormSet(queryset = query_set)
        formset.forms[0].fields['value'] = \
            forms.ModelChoiceField(queryset=Actor.objects.all())

    return render_to_response("crptapp/question_detail.html", {
    "formset": formset,
    }, context_instance=RequestContext(request))

@login_required
def get_ra_question_statements(request, ra_question_id, ra_section_id,
                               assessment_id):
    """
    View for ra question statements
    :param request:
    :param ra_question_id:
    :param ra_section_id:
    :param assessment_id:
    :return:
    """
    assessment = Assessment.objects.get(pk=assessment_id)
    ra_section = RiskAssessmentSection.objects.get(pk=ra_section_id)
    RAQuestionStatmentFormSet = \
        modelformset_factory(AssessmentRAQuestionStatement,
                             max_num=len(assessment.hazards.all()))

    question_statement = \
        AssessmentRAQuestionStatement.objects.get(pk = ra_question_id)
    files_to_show = \
        ('short_term_value','mid_term_value','long_term_value','mov')

    if request.method == 'POST':
        formset = RAQuestionStatmentFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            ra_questionset_list = \
                RiskAssessmentQuestionset.objects.filter(ra_section =
                                                         ra_section_id)
            question_list = \
                RiskAssessmentQuestion.objects.filter(ra_questionset =
                                                      ra_questionset_list).\
                    order_by('id')
            paginator = Paginator(question_list, 25) # Show 25 items per page
            page = request.GET.get('page')
            try:
                questions = paginator.page(page)
            except:
                questions = paginator.page(1)
            return render_to_response('crptapp/ra_questions.html',
                                      {"questions": questions,
                                       "assessment":assessment,
                                       "ra_section":ra_section,})
        else:
            if format(len(formset.errors) > 0):
                num_errors = len(formset.errors[0])
        set_ra_statements_hidden_fields(formset, files_to_show)
        #set_ra_statements_readonly_fields(formset)
    else:
        query_set = AssessmentRAQuestionStatement.objects.filter(
            ra_question = ra_question_id).order_by('hazard')
        formset = RAQuestionStatmentFormSet(queryset = query_set)
        set_ra_statements_hidden_fields(formset, files_to_show)
        #set_ra_statements_readonly_fields(formset)
    formset.is_valid()

    return render_to_response("crptapp/question_detail.html", {
    "formset": formset,
    "description":question_statement.ra_question.description,
    "assessment":assessment,
    "ra_section":ra_section,
    }, context_instance=RequestContext(request))

@login_required
def get_causality_matrix_questions(request, assessment_id, ra_question_id):
    """
    View to get ra causality matrix questions
    :param request:
    :param assessment_id:
    :param ra_question_id:
    :return:
    """
    assessment = Assessment.objects.get(pk=assessment_id)
    CausalityMatrixFormSet = \
        modelformset_factory(AssessmentHazardCausality,
            max_num= len(assessment.hazards.all()))
    ra_question = RiskAssessmentQuestion.objects.get(pk=ra_question_id)
    files_to_show = ('short_term_value','mid_term_value','long_term_value','mov')

    if request.method == 'POST':
        formset = CausalityMatrixFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            return render_to_response("crptapp/assessments.html",
                {'assessment_list':Assessment.objects.all()})
        else:
            if format(len(formset.errors) > 0):
                num_errors = len(formset.errors[0])
        set_ra_statements_hidden_fields(formset, files_to_show)
    else:
        query_set = \
            AssessmentHazardCausality.objects.filter(assessment =
                                                     assessment_id).\
                order_by('hazard_occurrence')
        formset = CausalityMatrixFormSet(queryset = query_set)
        set_ra_statements_hidden_fields(formset, files_to_show)
        #set_ra_statements_readonly_fields(formset)
    formset.is_valid()

    return render_to_response("crptapp/ra_causality_question_detail.html", {
    "formset": formset,
    "description":ra_question.description
    }, context_instance=RequestContext(request))

@login_required
def get_ca_statement(request, assessment_id, hazard_id, statement_id):
    """
    View for ca statement form
    :param request:
    :param assessment_id:
    :param hazard_id:
    :param statement_id:
    :return:
    """
    assessment = Assessment.objects.get(pk=assessment_id)
    statement = AssessmentCAQuestionStatement.objects.get(pk=statement_id)
    statement_description = statement.ca_statement.description
    ca_subsection = statement.ca_questionset.ca_subsection
    ca_section = ca_subsection.ca_section
    hazard = Hazard.objects.get(pk=hazard_id)

    CAStatementFormSet = modelformset_factory(AssessmentCAQuestionStatement,
                                              max_num=1)
    files_to_show=('values','mov')

    if request.method == 'POST':
        formset = CAStatementFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            # Form ok. Back to list
            return get_ca_subsection_questions_by_hazard(request,
                                                         assessment.id,
                                                         ca_subsection.id,
                                                         hazard.id)

        else:
            if format(len(formset.errors) > 0):
                num_errors = len(formset.errors[0])
            set_ra_statements_hidden_fields(formset, files_to_show)
            set_option_values(statement, formset)
    else:
        query_set = AssessmentCAQuestionStatement.objects.filter(id=
                                                                 statement_id)
        formset = CAStatementFormSet(queryset=query_set)
        set_ra_statements_hidden_fields(formset, files_to_show)
        set_option_values(statement, formset)


    return render_to_response("crptapp/question_detail.html", {
    "formset": formset,
    "description": statement_description,
    "assessment":assessment,
    "ca_section":ca_section,
    "ca_subsection":ca_subsection,
    "hazard":hazard,
    }, context_instance=RequestContext(request))

@login_required
def get_ca_statement_by_assessment_question(request, assessment_id,
                                            question_id):
    """
    View for ca statement by question
    :param request:
    :param assessment_id:
    :param question_id:
    :return:
    """
    assessment = Assessment.objects.get(pk=assessment_id)
    question = CapacityAssessmentQuestion.objects.get(pk=question_id)

    # OBS: !! Works if there is 1! statement for question
    query_set = AssessmentCAQuestionStatement.objects.filter(assessment=
        assessment_id, ca_question=question_id).order_by('ca_question','id')
    statement =  query_set[0]
    #
    description = question.description
    ca_subsection = question.ca_questionset.ca_subsection
    ca_section = ca_subsection.ca_section
    CAGenericStatmentFormSet = \
        modelformset_factory(AssessmentCAQuestionStatement,max_num=1)
    files_to_show=('values','mov')

    if request.method == 'POST':
        formset = CAGenericStatmentFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()

            return get_ca_subsection_questions(request, ca_section.id,
                                               ca_subsection.id,
                                assessment.id)

        else:
            if format(len(formset.errors) > 0):
                num_errors = len(formset.errors[0])
            set_ra_statements_hidden_fields(formset, files_to_show)
            set_option_values(statement, formset)
    else:
        query_set = AssessmentCAQuestionStatement.objects.filter(assessment=
            assessment_id, ca_question=question_id).order_by('ca_question','id')
        formset = CAGenericStatmentFormSet(queryset = query_set)
        set_ra_statements_hidden_fields(formset, files_to_show)
        set_option_values(statement, formset)

    return render_to_response("crptapp/question_detail.html", {
    "formset": formset,
    "description": description,
    "assessment":assessment,
    "ca_section":ca_section,
    "ca_subsection":ca_subsection,
    }, context_instance=RequestContext(request))


def set_ra_statements_hidden_fields(formset, files_to_show):
    """
    Function to set hidden fields and show fields of each form in formset
    :param formset:
    :param files_to_show:
    :return:
    """
    #files_to_show = ('short_term_value','mid_term_value','long_term_value','mov')
    for form in formset:
        for field in form.fields:
            if not any(field in s for s in files_to_show):
                form.fields[field].widget = forms.HiddenInput()

def set_ra_statements_readonly_fields(formset):
    """
    Function to set readonly fields of each form in formset
    :param formset:
    :return:
    """
    read_only_fields = ('hazard',)
    for form in formset:
        for field in form.fields:
            print(field)
            if any(field in s for s in read_only_fields):
                print(field)
                form.fields[field].widget.attrs['disabled'] = True


def set_option_values(statement, formset):
    """
    Function to set values for each statement type
    :param statement:
    :param formset:
    :return:
    """
    if(statement.ca_statement.statement_type == "MFH"):
        formset.forms[0].fields['value'] = forms.ModelChoiceField(
            queryset=MeetingFrequencyValues.objects.all())
    elif(statement.ca_statement.statement_type == "MAH"):
        formset.forms[0].fields['value'] = forms.ModelChoiceField(
            queryset=MeetingAttendanceValues.objects.all())
    elif(statement.ca_statement.statement_type == "MFH"):
        formset.forms[0].fields['value'] = forms.ModelChoiceField(
            MeetingFrequencyValues.objects.all())
    elif(statement.ca_statement.statement_type == "EFH"):
        formset.forms[0].fields['value'] = forms.ModelChoiceField(
            EffectivenessValues.objects.all())
    else:
        formset.forms[0].fields['value'] = forms.ModelChoiceField(
            YesNoValues.objects.all())