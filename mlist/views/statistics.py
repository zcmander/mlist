from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response

@login_required()
def statistics_view(request):
    return render_to_response("mlist/statistics.html")
