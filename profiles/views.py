from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from .forms import CustomPasswordChangeForm

from accounts.models import User, Person, Counselor, CustomerSupport


@login_required(redirect_field_name='login')
def password_check_view(request):
    user = request.user

    if request.method == 'POST':
        login_id = user.login_id
        login_pw = request.POST['login_pw']
        user = authenticate(request, login_id=login_id, password=login_pw)

        if user is not None:
            return redirect('profile')  # 인증 성공 시 프로필 페이지로 이동
        else:
            messages.error(request, "비밀번호가 올바르지 않습니다.")  # 오류 메시지 추가

    return render(request, "profile/password_check.html")

@login_required(redirect_field_name='login')
def profile_home(request):
    user = request.user
    person = Person.objects.get(pk=user.pk)

    if person.role == 'user':
        userdata = User.objects.get(pk=user.pk)
        return render(request, "profile/profile.html", {
            "user": user,
            "person": person,
            "userdata": userdata,
            "role": "사용자",
        })
    elif person.role == 'counselor':
        userdata = Counselor.objects.get(pk=user.pk)
        contact = Person.objects.get(pk=userdata.admin_id)
        return render(request, "profile/profile.html", {
            "user": user,
            "person": person,
            "userdata": userdata,
            "contact": contact,
            "role": "상담사",
        })
    elif person.role == 'customer_support':
        userdata = CustomerSupport.objects.get(pk=user.pk)
        contact = Person.objects.get(pk=userdata.admin_id)
        return render(request, "profile/profile.html", {
            "user": user,
            "person": person,
            "userdata": userdata,
            "contact": contact,
            "role": "고객 담당자",
        })

    # 사용자 정보를 템플릿에 전달
    return render(request, "profile/profile.html", {
        "user": user,
        "person": person,
        "role": "관리자",
    })


class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'profile/password_change.html'
    success_url = '/profile/password-change-done/'