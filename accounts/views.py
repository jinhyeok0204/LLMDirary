from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from accounts.models import Person, User, Counselor, CustomerSupport
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password


def login_view(request):
    if request.method == 'POST':
        login_id = request.POST['login_id']
        login_pw = request.POST['login_pw']
        user = authenticate(request, login_id=login_id, password=login_pw)

        if user is not None:
            # 로그인 성공
            login(request, user)
            messages.success(request, "로그인에 성공했습니다.")
            request.session['user_id'] = user.id

            # 역할에 따른 redirect
            try:
                person = Person.objects.get(pk=user.pk)
                if person.role == 'admin':
                    return redirect('admin_dashboard')
                elif person.role == 'customer_support':
                    return redirect('customer_support_dashboard')
                elif person.role == 'counselor':
                    return redirect('counselor_dashboard')
                else: # user
                    return redirect('home')
            except Person.DoesNotExist:
                messages.error(request, "사용자 정보에 문제가 있습니다.")
                return redirect('login')
        else:
            messages.error(request, "로그인 ID 또는 비밀번호가 잘못되었습니다.")
            return redirect('login')

    return render(request, 'accounts/login.html')


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
    messages.success(request, "로그아웃 되었습니다.")
    return redirect('login')


# 사용자 대시보드 (User 전용)
@login_required
def user_home(request):
    person = Person.objects.get(id=request.user.id)
    if person.role != 'user':
        return HttpResponseForbidden("일반 사용자만 접근 가능합니다.")

    user = User.objects.get(id=person)
    return render(request, 'user/home.html', {'person': person, 'user': user})


# 관리자 대시보드 (Admin 전용)
@login_required
def admin_dashboard(request):
    person = request.user
    person = Person.objects.get(id=request.user.id)
    if not person.is_admin():
        return HttpResponseForbidden("관리자만 접근 가능합니다.")

    # 관리자 관련 데이터
    counselors = Counselor.objects.filter(admin=person)
    customer_supports = CustomerSupport.objects.filter(admin=person)
    return render(request, 'accounts/admin_dashboard.html', {
        'person': person,
        'counselors': counselors,
        'customer_supports': customer_supports,
    })


# 상담사 대시보드 (Counselor 전용)
@login_required
def counselor_dashboard(request):
    person = Person.objects.get(id=request.user.id)
    if person.role != 'counselor':
        return HttpResponseForbidden("상담사만 접근 가능합니다.")

    counselor = Counselor.objects.get(id=person)
    return render(request, 'accounts/counselor_dashboard.html', {'person': person, 'counselor': counselor})


# 고객 지원 대시보드 (Customer Support 전용)
@login_required
def customer_support_dashboard(request):
    person = Person.objects.get(id=request.user.id)
    if person.role != 'customer_support':
        return HttpResponseForbidden("고객 지원 담당자만 접근 가능합니다.")

    customer_support = CustomerSupport.objects.get(id=person)
    return render(request, 'accounts/customer_support_dashboard.html',
                  {'person': person, 'customer_support': customer_support})


