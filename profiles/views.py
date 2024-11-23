from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib import messages

from accounts.models import User, Person

@login_required(redirect_field_name='login')
def password_check_view(request):
    if request.method == 'POST':
        login_id = request.session['login_id']
        login_pw = request.POST['login_pw']
        user = authenticate(request, login_id=login_id, password=login_pw)

        if user is not None:
            return redirect('profile')  # 인증 성공 시 프로필 페이지로 이동
        else:
            messages.error(request, "비밀번호가 올바르지 않습니다.")  # 오류 메시지 추가

    return render(request, "profile/password_check.html")
def profile_home(request):
    user = request.user

    person = Person.objects.get(pk=user.pk)
    userdata = User.objects.get(pk=user.pk)

    # 사용자 정보를 템플릿에 전달
    return render(request, "profile/profile.html", {
        "user": user,
        "person": person,
        "userdata": userdata,
    })

