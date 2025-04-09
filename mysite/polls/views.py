from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.db import connection
from django.utils import timezone

from .models import Choice, Question

def index(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    context = {"latest_question_list": latest_question_list}
    return render(request, "polls/index.html", context)
    
    
def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/detail.html", {"question": question})


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/results.html", {"question": question})
    
    
def create_poll(request):
    if request.method == 'POST':
    	question_text = request.POST['question_text']
    	choices = [request.POST["1choice"], request.POST["2choice"], request.POST["3choice"],]
    	
    	
    	
    	#Below is SQl Injection flaw (rows 34-35)
    	with connection.cursor() as cursor:
    		cursor.execute(f"INSERT INTO polls_question (question_text, pub_date) VALUES ('{question_text}', '{timezone.now()}')")
    	# To fix this flaw (row 37)
    	# Question.objects.create(question_text=question_text, pub_date=timezone.now())
    
    
    
    
    	latest_question = Question.objects.latest("id")
    	for choice in choices:
    		Choice.objects.create(question=latest_question, choice_text=choice, votes=0)
    	
    	return HttpResponseRedirect(reverse("polls:index"))
    	
    return HttpResponse("error")
    
    

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
