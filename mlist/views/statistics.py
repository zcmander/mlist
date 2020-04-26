from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required()
def statistics_view(request):
    render_dict = {
        'user': request.user,
    }
    return render(request, "mlist/statistics.html", render_dict)
