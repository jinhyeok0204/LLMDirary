from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from accounts.models import Person, User, Counselor, CustomerSupport
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.sessions.models import Session


def login_view(request):
    if request.method == 'POST':
        login_id = request.POST['login_id']
        login_pw = request.POST['login_pw']
        user = authenticate(request, login_id=login_id, password=login_pw)

        if user is not None:
            try:
                # Person 객체를 먼저 가져옴
                person = Person.objects.get(pk=user.pk)

                # 조건에 따라 관련 모델을 로드
                if person.role == 'counselor':
                    counselor = Counselor.objects.select_related('id').get(id=person)
                    if not counselor.is_approved:
                        messages.error(request, "승인되지 않은 상담사 계정입니다. 관리자에게 문의하세요.")
                        return redirect('login')

                elif person.role == 'customer_support':
                    customer_support = CustomerSupport.objects.select_related('id').get(id=person)
                    if not customer_support.is_approved:
                        messages.error(request, "승인되지 않은 고객 지원 계정입니다. 관리자에게 문의하세요.")
                        return redirect('login')

                # 로그인 성공
                login(request, user)
                messages.success(request, "로그인에 성공했습니다.")

                # 역할에 따른 redirect
                if person.role == 'admin':
                    return redirect('admin_home')
                elif person.role == 'customer_support':
                    return redirect('customer_support_home')
                elif person.role == 'counselor':
                    return redirect('counselor_home')
                else: # user
                    return redirect('home')

            except(Person.DoesNotExist, Counselor.DoesNotExist, CustomerSupport.DoesNotExist):
                messages.error(request, "사용자 정보에 문제가 있습니다.")
                return redirect('login')

        else:
            messages.error(request, "로그인 ID 또는 비밀번호가 잘못되었습니다.")
            return redirect('login')

    return render(request, 'accounts/login.html')


@transaction.atomic
def signup_view(request):
    if request.method == 'POST':
        # 공통 필드 가져오기
        name = request.POST.get('name', '').strip()
        login_id = request.POST.get('login_id', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        phone_num = request.POST.get('phone_num', '').strip()
        role = request.POST.get('role', '').strip()

        # 비밀번호 확인
        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        # 중복된 Login ID 확인
        if Person.objects.filter(login_id=login_id).exists():
            messages.error(request, "Login ID already exists.")
            return redirect('signup')

        # 역할에 따른 추가 필드 확인 및 유효성 검사
        if role == 'user':
            birth = request.POST.get('birth', '').strip()
            gender = request.POST.get('gender', '').strip()
            if not birth or not gender:
                messages.error(request, "Birth date and gender are required for Users.")
                return redirect('signup')
        elif role == 'counselor':
            gender = request.POST.get('gender', '').strip()
            if not gender:
                messages.error(request, "Gender is required for Counselors.")
                return redirect('signup')

        # Person 객체 생성
        person = Person.objects.create(
            name=name,
            login_id=login_id,
            password=make_password(password),
            phone_num=phone_num,
            role=role,
            is_staff=(role == 'admin') # Admin일 경우에만 관리자 권한 부여
        )

        # 역할에 따라 객체 생성
        if role == 'user':
            User.objects.create(id=person, gender=gender, birth=birth)
        elif role == 'counselor':
            Counselor.objects.create(id=person, gender=gender)
        elif role == 'customer_support':
            CustomerSupport.objects.create(id=person, salary=0)

        # 성공 메시지 및 리다이렉션
        messages.success(request, "Account created successfully. Please log in.")
        return redirect('login')

    return render(request, 'accounts/signup.html')


# 로그아웃 뷰
@login_required
def logout_view(request):
    logout(request)
    Session.objects.all().delete()
    messages.success(request, "로그아웃 되었습니다.")
    return redirect('login')
