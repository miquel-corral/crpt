from django.shortcuts import render
from django.views import generic
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from forms import AssessmentForm
from models import Assessment, RiskAssessmentSection, CapacityAssessmentSection, AssessmentRAQuestionStatement, \
     Actor, RiskAssessmentQuestion, Hazard, \
    RiskAssessmentQuestionset, AssessmentHazardCausality, CapacityAssessmentQuestionSet, CapacityAssessmentQuestion, \
    CapacityAssessmentStatement, AssessmentCAQuestionStatement
from django.shortcuts import render_to_response
from django.forms.models import modelformset_factory
from django.contrib.admin.widgets import AdminDateWidget
from django import forms
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.core.context_processors import csrf
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class IndexView(generic.ListView):
    template_name = 'crptapp/index.html'
    context_object_name = 'assessment_list'

    def get_queryset(self):
        """Return the assessments"""
        return Assessment.objects.order_by('name')

class AssessmentDetailView(generic.DetailView):
    model = Assessment
    template_name = 'crptapp/assessment_detail.html'


@ensure_csrf_cookie
def getAssessmentForm(request, assessment_id=None, assessment_name=None):
    AssessmentFormSet = modelformset_factory(Assessment,max_num=1,
                                         widgets={'initial_date': forms.TextInput(attrs={'class':'vDateField'}),
                                                  'final_date': forms.TextInput(attrs={'class':'vDateField'}),
                                                  'last_update': forms.HiddenInput()
                                                  })
    num_errors = 0
    if request.method == 'POST':
        print("POPOROTOTO")
        formset = AssessmentFormSet(request.POST, request.FILES)
        if formset.is_valid():
            print("POPOROTOTOPERO")
            formset.save()
            return render_to_response("crptapp/index.html", {'assessment_list':Assessment.objects.all()})
        else:
            if format(len(formset.errors) > 0):
                num_errors = len(formset.errors[0])
    else:
        formset = AssessmentFormSet(queryset=Assessment.objects.filter(pk=assessment_id))
    return render_to_response("crptapp/assessment_detail.html", {
    "formset": formset,
    "num_errors":num_errors,
    "assessment_name":assessment_name}, context_instance=RequestContext(request))


def assessmentIndex(request):
    """

    :param request:
    :return:
    """
    assessments = Assessment.objects.all()
    ra_sections = RiskAssessmentSection.objects.all()
    ca_sections = CapacityAssessmentSection.objects.all()
    template = loader.get_template('crptapp/index.html')
    context = RequestContext(request, {
        'assessments': assessments,
        'ra_sections': ra_sections,
        'ca_sections': ca_sections,
    })
    return HttpResponse(template.render(context))


def getRASectionQuestions(request, ra_section_id, assessment_id):
    """

    :param request:
    :param ra_section_id:
    :param assessment_id:
    :return:
    """
    questions = AssessmentRAQuestionStatement.objects.filter(assessment=assessment_id, ra_section=ra_section_id);
    template = loader.get_template('crptapp/ra_questions.html')
    context = RequestContext(request, {
        'questions':questions
    })
    return HttpResponse(template.render(context))


def getCASubsectionQuestions(request, ca_section_id, ca_subsection_id, assessment_id):
    """

    :param request:
    :param ra_section_id:
    :param assessment_id:
    :return:
    """

    """
    assessment = Assessment.objects.get(pk=assessment_id)
    ca_question_list = []
    ca_questionset_list = CapacityAssessmentQuestionSet.objects.filter(ca_subsection_id=ca_subsection_id).order_by('ca_subsection','code')
    for ca_questionset in ca_questionset_list:
        ca_question_list.extend(CapacityAssessmentQuestion.objects.filter(ca_questionset=ca_questionset).order_by('ca_questionset','code'))
    """
    # only questions not hazard-related

    assessment = Assessment.objects.get(pk=assessment_id)

    print("HAZARDS {}".format(assessment.hazards.all().count()))

    ca_question_list = []
    num_hazard_related_questions = 0
    ca_questionset_list = CapacityAssessmentQuestionSet.objects.filter(ca_subsection_id=ca_subsection_id).order_by('ca_subsection','code')
    for ca_questionset in ca_questionset_list:
        # exclusion in filter is_by_hazard
        ca_question_list.extend(CapacityAssessmentQuestion.objects.filter(ca_questionset=ca_questionset, is_by_hazard=False).order_by('ca_questionset','code'))
        # check if any question hazard-related
        num_hazard_related_questions += CapacityAssessmentQuestion.objects.filter(ca_questionset=ca_questionset, is_by_hazard=True).count()

    paginator = Paginator(ca_question_list, 25) # Show 25 items per page
    page = request.GET.get('page')
    try:
        questions = paginator.page(page)
    except:
        questions = paginator.page(1)
    return render_to_response('crptapp/ca_questions.html', {"questions": questions,\
                                                            "assessment":assessment, \
                                                            "num_hazard_related_questions":num_hazard_related_questions\
        ,"ca_subsection_id":ca_subsection_id})

def getCASubsectionQuestionsByHazard(request, assessment_id,  ca_subsection_id, hazard_id):

    assessment = Assessment.objects.get(pk=assessment_id)
    # selection of question statements, no questions, to show each description
    ca_question_list = AssessmentCAQuestionStatement.objects.filter(assessment=assessment_id,
                                                                       ca_subsection=ca_subsection_id,\
                                                                       hazard=hazard_id).order_by('ca_subsection',\
                                                                                                  'ca_question',
                                                                                                  'id')

    paginator = Paginator(ca_question_list, 25) # Show 25 items per page
    page = request.GET.get('page')
    try:
        questions = paginator.page(page)
    except:
        questions = paginator.page(1)
    return render_to_response('crptapp/ca_questions_by_hazard.html', {"questions": questions, "assessment":assessment})



def getRASectionQuestionsPaginated(request, ra_section_id, assessment_id):

    assessment = Assessment.objects.get(pk=assessment_id)
    ra_questionset_list = RiskAssessmentQuestionset.objects.filter(ra_section=ra_section_id)
    question_list = RiskAssessmentQuestion.objects.filter(ra_questionset=ra_questionset_list).order_by('id')
    paginator = Paginator(question_list, 25) # Show 25 items per page
    page = request.GET.get('page')
    try:
        questions = paginator.page(page)
    except:
        questions = paginator.page(1)
    return render_to_response('crptapp/ra_questions.html', {"questions": questions,"assessment":assessment})



@ensure_csrf_cookie
def getCAGenericStatementForm(request, statement_id):
    CAGenericStatmentFormSet = modelformset_factory(AssessmentCAQuestionStatement,max_num=1)

    if request.method == 'POST':
        formset = CAGenericStatmentFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            return render_to_response("crptapp/index.html", {'assessment_list':Assessment.objects.all()})
        else:
            if format(len(formset.errors) > 0):
                num_errors = len(formset.errors[0])
            formset.forms[0].fields['value'] = forms.ModelChoiceField(queryset=Actor.objects.all())
    else:
        formset = CAGenericStatmentFormSet(queryset=AssessmentCAQuestionStatement.objects.filter(pk=statement_id))
        formset.forms[0].fields['value'] = forms.ModelChoiceField(queryset=Actor.objects.all())

    return render_to_response("crptapp/ra_question_detail.html", {
    "formset": formset,
    }, context_instance=RequestContext(request))



def getRAQuestionStatements(request, ra_question_id, ra_section_id, assessment_id):
    assessment = Assessment.objects.get(pk=assessment_id)
    RAQuestionStatmentFormSet = modelformset_factory(AssessmentRAQuestionStatement,max_num=len(assessment.hazards.all()))
    #RAQuestionStatmentFormSet = modelformset_factory(AssessmentRAQuestionStatement,max_num=1)
    question_statement = AssessmentRAQuestionStatement.objects.get(pk=ra_question_id)
    files_to_show = ('short_term_value','mid_term_value','long_term_value','mov')

    if request.method == 'POST':
        formset = RAQuestionStatmentFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            return render_to_response("crptapp/index.html", {'assessment_list':Assessment.objects.all()})
        else:
            if format(len(formset.errors) > 0):
                num_errors = len(formset.errors[0])
        set_ra_statements_hidden_fields(formset, files_to_show)
    else:
        formset = RAQuestionStatmentFormSet(queryset=AssessmentRAQuestionStatement.objects.filter(ra_question=ra_question_id).order_by('hazard'))
        set_ra_statements_hidden_fields(formset, files_to_show)
        set_ra_statements_readonly_fields(formset)
    formset.is_valid()

    return render_to_response("crptapp/ra_question_detail.html", {
    "formset": formset,
    "description":question_statement.ra_question.description
    }, context_instance=RequestContext(request))


def getCausalityMatrixQuestions(request, assessment_id, ra_question_id):
    assessment = Assessment.objects.get(pk=assessment_id)
    CausalityMatrixFormSet = modelformset_factory(AssessmentHazardCausality,max_num=len(assessment.hazards.all()))
    ra_question = RiskAssessmentQuestion.objects.get(pk=ra_question_id)
    files_to_show = ('short_term_value','mid_term_value','long_term_value','mov')

    if request.method == 'POST':
        formset = CausalityMatrixFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            return render_to_response("crptapp/index.html", {'assessment_list':Assessment.objects.all()})
        else:
            if format(len(formset.errors) > 0):
                num_errors = len(formset.errors[0])
        set_ra_statements_hidden_fields(formset, files_to_show)
    else:
        formset = CausalityMatrixFormSet(queryset=AssessmentHazardCausality.objects.filter(assessment=assessment_id).order_by('hazard_occurrence'))
        set_ra_statements_hidden_fields(formset, files_to_show)
        #set_ra_statements_readonly_fields(formset)
    formset.is_valid()

    return render_to_response("crptapp/ra_causality_question_detail.html", {
    "formset": formset,
    "description":ra_question.description
    }, context_instance=RequestContext(request))

def getCAStatement(request, statement_id):

    statement_description = AssessmentCAQuestionStatement.objects.get(pk=statement_id).ca_statement.description

    CAStatementFormSet = modelformset_factory(AssessmentCAQuestionStatement,max_num=1)
    files_to_show=('values','mov')

    if request.method == 'POST':
        formset = CAStatementFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            return render_to_response("crptapp/index.html", {'assessment_list':Assessment.objects.all()})
        else:
            if format(len(formset.errors) > 0):
                num_errors = len(formset.errors[0])
            # TODO: tractament per a tots els forms amb select option fields
            set_ra_statements_hidden_fields(formset, files_to_show)
            #formset.forms[0].fields['value'] = forms.ModelChoiceField(queryset=ValueListType.objects.get(pk=formset.forms[0].fields['value_list_type']))
            # TODO:
            # Model ValueListType (id, value_class)
            # Models per cada tipus de llista: Yes/No, Meeting Frequency, etc..
            # En la creació dels assessment_statements mirar de setejar llista pel tipus statement.
            # Si no es pot fer-ho aqui, pre-omplint un dictionary ["value_list_type","value_class"]
            # I fent lookup del value list a assignar al widget per value_list_type["value_class"]
    else:
        formset = CAStatementFormSet(queryset=AssessmentCAQuestionStatement.objects.filter(id=statement_id))
        set_ra_statements_hidden_fields(formset, files_to_show)
        # TODO: tractament per a tots els forms amb select option fields
        #formset.forms[0].fields['value'] = forms.ModelChoiceField(queryset=Actor.objects.all())

    return render_to_response("crptapp/ra_question_detail.html", {
    "formset": formset,
    "description": statement_description
    }, context_instance=RequestContext(request))


def getCAStatementByAssessmentQuestion(request,assessment_id, question_id):
    assessment = Assessment.objects.get(pk=assessment_id)
    description = CapacityAssessmentQuestion.objects.get(pk=question_id).description
    CAGenericStatmentFormSet = modelformset_factory(AssessmentCAQuestionStatement,max_num=1)
    files_to_show=('values','mov')

    if request.method == 'POST':
        formset = CAGenericStatmentFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            return render_to_response("crptapp/index.html", {'assessment_list':Assessment.objects.all()})
        else:
            if format(len(formset.errors) > 0):
                num_errors = len(formset.errors[0])
            set_ra_statements_hidden_fields(formset, files_to_show)
            # TODO: tractament per a tots els forms amb select option fields
            #formset.forms[0].fields['value'] = forms.ModelChoiceField(queryset=Actor.objects.all())
    else:
        formset = CAGenericStatmentFormSet(queryset=AssessmentCAQuestionStatement.objects.filter(assessment=assessment_id, ca_question=question_id).order_by('ca_question','id'))
        set_ra_statements_hidden_fields(formset, files_to_show)
        # TODO: tractament per a tots els forms amb select option fields
        #formset.forms[0].fields['value'] = forms.ModelChoiceField(queryset=Actor.objects.all())

    return render_to_response("crptapp/ra_question_detail.html", {
    "formset": formset,
    "description": description
    }, context_instance=RequestContext(request))

def set_ra_statements_hidden_fields(formset, files_to_show):
    #files_to_show = ('short_term_value','mid_term_value','long_term_value','mov')
    for form in formset:
        for field in form.fields:
            if not any(field in s for s in files_to_show):
                form.fields[field].widget = forms.HiddenInput()

def set_ra_statements_readonly_fields(formset):
    read_only_fields = ('hazard',)
    for form in formset:
        for field in form.fields:
            print(field)
            if any(field in s for s in read_only_fields):
                print(field)
                form.fields[field].widget.attrs['disabled'] = True


