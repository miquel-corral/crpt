from django.shortcuts import render
from django.views import generic
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from forms import AssessmentForm
from models import Assessment, RiskAssessmentSection, CapacityAssessmentSection, AssessmentRAQuestionStatement, \
    AssessmentCAYESNOStatement, AssessmentCAGenericStatement, Actor, RiskAssessmentQuestion, Hazard, RiskAssessmentQuestionset
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
    questions = AssessmentCAYESNOStatement.objects.all();
    template = loader.get_template('crptapp/ca_questions.html')
    context = RequestContext(request, {
        'questions':questions
    })
    return HttpResponse(template.render(context))



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
    CAGenericStatmentFormSet = modelformset_factory(AssessmentCAGenericStatement,max_num=1)


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
        formset = CAGenericStatmentFormSet(queryset=AssessmentCAGenericStatement.objects.filter(pk=statement_id))
        formset.forms[0].fields['value'] = forms.ModelChoiceField(queryset=Actor.objects.all())

    return render_to_response("crptapp/ca_generic_statement_detail.html", {
    "formset": formset,
    }, context_instance=RequestContext(request))



def getRAQuestionStatements(request, ra_question_id, ra_section_id, assessment_id):
    assessment = Assessment.objects.get(pk=assessment_id)
    RAQuestionStatmentFormSet = modelformset_factory(AssessmentRAQuestionStatement,max_num=len(assessment.hazards.all()))
    #RAQuestionStatmentFormSet = modelformset_factory(AssessmentRAQuestionStatement,max_num=1)
    question_statement = AssessmentRAQuestionStatement.objects.get(pk=ra_question_id)

    if request.method == 'POST':
        formset = RAQuestionStatmentFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            return render_to_response("crptapp/index.html", {'assessment_list':Assessment.objects.all()})
        else:
            if format(len(formset.errors) > 0):
                num_errors = len(formset.errors[0])
        set_ra_statements_hidden_fields(formset)
    else:
        formset = RAQuestionStatmentFormSet(queryset=AssessmentRAQuestionStatement.objects.filter(ra_question=ra_question_id).order_by('hazard'))
        set_ra_statements_hidden_fields(formset)
        #set_ra_statements_readonly_fields(formset)
    formset.is_valid()

    return render_to_response("crptapp/ra_question_detail.html", {
    "formset": formset,
    "description":question_statement.ra_question.description
    }, context_instance=RequestContext(request))


def set_ra_statements_hidden_fields(formset):
    files_to_show = ('short_term_value','mid_term_value','long_term_value','mov')
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