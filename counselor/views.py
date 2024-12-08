from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from datetime import date, timedelta
from calendar import Calendar
from counsel.models import Counsel
from accounts.models import Person, Counselor


# 상담사 홈 뷰
@login_required(redirect_field_name='login')
def counselor_home(request):
    person = Person.objects.get(id=request.user.id)
    if person.role != 'counselor':
        messages.error(request, "상담사만 접근 가능합니다.")
        return HttpResponseForbidden("상담사만 접근 가능합니다.")

    counselor = Counselor.objects.get(id=person)

    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    # 이전/다음 달 계산
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    start_date = date(year, month, 1)
    last_day = (start_date.replace(month=start_date.month % 12 + 1) - timedelta(days=1)).day
    end_date = date(year, month, last_day)

    schedules = Counsel.objects.filter(
        counselor=counselor,
        counsel_datetime__date__gte=start_date,
        counsel_datetime__date__lte=end_date
    )

    schedule_dict = {}
    for schedule in schedules:
        day = schedule.counsel_datetime.day
        if day not in schedule_dict:
            schedule_dict[day] = []
        schedule_dict[day].append(schedule)

    calendar = Calendar()
    days = [
        (day if day > 0 else 0, (idx + start_date.weekday()) % 7)
        for idx, day in enumerate(calendar.itermonthdays(year, month))
    ]

    return render(request, 'counselor/home.html', {
        'person': person,
        'counselor': counselor,
        'year': year,
        'month': month,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'days': days,
        'schedule_dict': schedule_dict,
    })
