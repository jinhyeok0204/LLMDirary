from django.shortcuts import render

# Create your views here.


def home_view(request):

    recent_diaries = Diary.objects.filter(user=request.user).order_by('-date')[:5]
    emotion_statistics = get_emotion_statistics(request.user)
    calendar_days = get_diary_calendar(request.user)

    return render(request, 'home/home.html', {
        'recent_diaries' : recent_diaries,
        'emotion_statistics' : emotion_statistics,
        'calendar_days': calendar_days
    })