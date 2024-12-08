from django.db.models import Count
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from accounts.models import Person, CustomerSupport
from diary.models import Diary
from django.utils.timezone import now, timedelta


@login_required(redirect_field_name='login')
def customer_support_home(request):
    person = Person.objects.get(id=request.user.id)

    if person.role != 'customer_support':
        messages.error(request, "고객 담당자만 접근 가능합니다.")
        return HttpResponseForbidden("고객 담당자만 접근 가능합니다.")

    # 최근 5일간의 날짜 계산
    five_days_ago = now() - timedelta(days=5)

    # 모든 사용자의 최근 5일간 일기 데이터 가져오기
    diaries = Diary.objects.filter(diary_date__gte=five_days_ago).order_by('diary_date')

    # 사용자별 최근 5일간 감정 분석 요약 통계
    emotion_frequencies = (
        Diary.objects.filter(diary_date__gte=five_days_ago)
        .values('user__id', 'emotion_analysis__summary')
        .annotate(count=Count('emotion_analysis__summary'))
    )

    # 사용자별 데이터 통계 저장
    user_emotion_data = {}
    for entry in emotion_frequencies:
        user_id = entry['user__id']
        summary = entry['emotion_analysis__summary']
        count = entry['count']

        if user_id not in user_emotion_data:
            user_emotion_data[user_id] = {}

        if summary not in user_emotion_data[user_id]:
            user_emotion_data[user_id][summary] = 0

        user_emotion_data[user_id][summary] += count

    return render(request, 'support/home.html', {
        'person': person,
        'diaries': diaries,
        'user_emotion_data': user_emotion_data,  # 사용자별 감정 데이터 추가
    })
