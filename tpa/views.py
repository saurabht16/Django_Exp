from django.http import HttpResponse, HttpResponseRedirect
from .models import Question, Choice
from django.template import loader
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.http import JsonResponse


class IndexView(generic.ListView):
    template_name = 'tpa/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'tpa/detail.html'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'tpa/results.html'


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'tpa/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('tpa:results', args=(question.id,)))

from dal import autocomplete

from tpa.models import newChoice


class newChoiceAutocomplete(autocomplete.Select2QuerySetView):
    print("Test123456")
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return newChoice.objects.none()

        qs = newChoice.objects.all()
        if self.forwarded.get('mychoice') is None:
            print("abcaaaaa")
        else:
            continent = self.forwarded.get('mychoice')
            abc = self.forwarded.get('newchoice')

        print(abc)
        print(continent)
        if continent:
            qs = qs.filter(id=continent)

        if self.q:
            qs = qs.filter(newquestion__istartswith=self.q)

        return qs

from .admin import Segmentation_Form

def country_form(request):
    # instead of hardcoding a list you could make a query of a model, as long as
    # it has a __str__() method you should be able to display it.
    country_list = ('Mexico', 'USA', 'China', 'France')
    form = FormForm(data_list=country_list)

    return render(request, 'my_app/country-form.html', {
        'form': form
    })


def home(request):
    title = "This is My Home page"
    context = {
        "page_title": title,
    }
    return render(request, "home.html", context)

def about(request):
    return render(request, "about.html", {})

def contact(request):
    return render(request, "contact.html", {})