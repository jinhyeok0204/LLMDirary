from collections import defaultdict

from django.shortcuts import render
from accounts.models import Person, Counselor
from diary.models import Diary
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from django.http import HttpResponseForbidden
from django.utils.timezone import now, timedelta
from django.db.models import Count


@login_required(redirect_field_name='login')
def home_view(request):
    if request.user.role != 'user':
        return HttpResponseForbidden("User만 접근 가능합니다.")

    user = request.user
    person = Person.objects.get(id=request.user.id)

    recent_diaries = Diary.objects.filter(user_id=user.id).order_by('diary_date')[:7]
    diaries = Diary.objects.filter(user=request.user.id).order_by('diary_date')

    one_month_ago = now() - timedelta(days=30)
    emotion_frequencies = (
        Diary.objects.filter(user=person.user, diary_date__gte=one_month_ago)
        .values('emotion_analysis__summary')
        .annotate(count=Count('emotion_analysis__summary'))
        .order_by('-count')
    )
    emotion_data = {entry['emotion_analysis__summary']: entry['count'] for entry in emotion_frequencies}

    return render(request, "user/home.html", {
        "user": user,
        "recent_diaries": recent_diaries,
        "emotion_data": emotion_data,
        "person_role": person.role,
        'diaries': diaries,
    })


@login_required()
def counselor_home(request):
    person = Person.objects.get(id=request.user.id)
    if person.role != 'counselor':
        messages.error(request, "상담사만 접근 가능합니다.")
        return HttpResponseForbidden("상담사만 접근 가능합니다.")

    counselor = Counselor.objects.get(id=person)
    return render(request, 'counselor/counselor_home.html', {
        'person': person,
        'counselor': counselor,
        "person_role": person.role,
    })

