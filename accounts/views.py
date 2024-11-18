from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from accounts.models import Person, User
# Create your views here.


def login_view(request):
    if request.method == 'POST':
        login_id = request.POST['login_id']
        login_pw = request.POST['login_pw']
        user = authenticate(request, login_id=login_id, login_pw=login_pw)

        if user is not None:
            login(request, user)
            messages.success(request, "로그인에 성공했습니다.")

            try:
                person = Person.objects.get(auth_user = user)
                if person.role == 'admin':
                    return redirect('admin_dashboard')
                elif person.role == 'customer_support':
                    return redirect('customer_support_dashboard')
                elif person.role == 'counselor':
                    return redirect('counselor_dashboard')
                else:
                    return redirect('user_home')
            except Person.DoesNotExist:
                messages.error(request, "사용자 정보에 문제가 있습니다.")
                return redirect('login')
        else:
            messages.error(request, "로그인 ID 또는 비밀번호가 잘못되었습니다.")
    return render(request, 'accounts/login.html')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']
        role = request.POST['role']

        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        # Django User 생성
        user = User.objects.create_user(username=username, password=password)

        # Person 객체 생성 및 role 지정
        Person.objects.create(auth_user=user, role=role)

        login(request, user)
        messages.success(request, "Account created successfully.")
        return redirect('user_home')  # 회원가입 성공 후 이동할 페이지
    return render(request, 'accounts/signup.html')