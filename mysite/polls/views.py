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

    # Flaw: Broken Access Control (url manipulation). For this, also the fix in vote() function needs to be implemented. 
    # Before the fix, people can go view the results of the poll before actually voting, by using /polls/id/results.
    # FIX: To fix this, we first made changes in vote() (added already_voted) and now we need to check if we have voted on the poll which results we are trying to see. See rows 26-28.
    #already_voted = request.session.get("already_voted", [])
    #if question_id not in already_voted:
    	#return HttpResponse("You must vote before you can see the results")

    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/results.html", {"question": question})
    
    
def create_poll(request):
    if request.method == 'POST':
    	question_text = request.POST['question_text']
    	choices = [request.POST["1choice"], request.POST["2choice"], request.POST["3choice"],]
    	
    	
    	
    	# Flaw: Below is SQl Injection flaw, see rows 42-43
    	with connection.cursor() as cursor:
    		cursor.executescript(f"INSERT INTO polls_question (question_text, pub_date) VALUES ('{question_text}', '{timezone.now()}')")
    	# FIX: see row 45
    	#Question.objects.create(question_text=question_text, pub_date=timezone.now())
    
    
    
    
    	latest_question = Question.objects.latest("id")
    	for choice in choices:
    		Choice.objects.create(question=latest_question, choice_text=choice, votes=0)
    	
    	return HttpResponseRedirect(reverse("polls:index"))
    	
    return HttpResponse("error")
    
    

def vote(request, question_id):
    # Flaw: Insecure Design. Below (uncommented vote() as a whole) you can uncontrollably vote on the same poll many times. 
    # FIX: To fix this without adding login function, we can help the situation by using sessions and tracking which polls have been aswered already. See rows 63-65 and 81-82.
    #already_voted = request.session.get("already_voted", [])
    #if question_id in already_voted:
    	#return HttpResponse("You can only vote ONCE on each poll!")
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
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
        #already_voted.append(question_id)
        #request.session["already_voted"] = already_voted
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
