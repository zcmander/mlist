from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response


@login_required()
def statistics_view(request):
    render_dict = {
        'user': request.user,
    }
    return render_to_response("mlist/statistics.html", render_dict)
