from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Diary
# Create your views here.

@login_required
def write_diary(request):
    if request.method == 'POST':
        diary_date = request.POST.get('diary_date')
        diary_content = request.POST.get('diary_content')

        # 유효성 검사
        if not diary_date or not diary_content:
            messages.error(request, "모든 필드를 입력해야 합니다.")
            return redirect('write_diary')

        # 중복 작성 방지
        if Diary.objects.filter(user=request.user, diary_date=diary_date).exists():
            messages.error(request, f"{diary_date}에 이미 작성된 일기가 있습니다.")
            return redirect('write_diary')

        # 다이어리 저장
        Diary.objects.create(
            user=request.user,
            diary_date=diary_date,
            diary_content=diary_content
        )

        messages.success(request, "다이어리가 성공적으로 작성되었습니다.")
        return redirect('user_home')  # 다이어리 작성 후 이동할 페이지

    return render(request, 'diary/write_diary.html')


def diary_home(request):
    return render(request, 'diary/diary_home.html')