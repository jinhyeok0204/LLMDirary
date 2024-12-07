from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.timezone import now
from accounts.models import Counselor
from .models import Counsel
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.core.paginator import EmptyPage
from django.contrib import messages

@login_required(redirect_field_name='login')
def counsel_home(request):
    user = request.user
    counsels = Counsel.objects.filter(user=user.id).select_related('counselor').order_by('counsel_date')
    counselors = Counselor.objects.filter(is_approved=True).select_related('id').order_by('id__name')

    # 페이지네이션 설정
    counsel_paginator = Paginator(counsels, 3)
    counsel_page_number = request.GET.get('counsel_page', 1)
    try:
        counsel_page_obj = counsel_paginator.get_page(counsel_page_number)
    except EmptyPage:
        counsel_page_obj = counsel_paginator.get_page(1)

    counselor_paginator = Paginator(counselors, 3)
    counselor_page_number = request.GET.get('counselor_page', 1)
    try:
        counselor_page_obj = counselor_paginator.get_page(counselor_page_number)
    except EmptyPage:
        counselor_page_obj = counselor_paginator.get_page(1)

    # AJAX 요청인지 확인
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if 'counsel_page' in request.GET:
            counsel_list = [
                {
                    'counselor_name': counsel.counselor.id.name,
                    'counsel_date': counsel.counsel_date.strftime('%Y년 %m월 %d일'),
                }
                for counsel in counsel_page_obj
            ]
            return JsonResponse({
                'counsels': counsel_list,
                'counsel_has_previous': counsel_page_obj.has_previous(),
                'counsel_has_next': counsel_page_obj.has_next(),
                'counsel_previous_page_number': counsel_page_obj.previous_page_number() if counsel_page_obj.has_previous() else None,
                'counsel_next_page_number': counsel_page_obj.next_page_number() if counsel_page_obj.has_next() else None,
                'counsel_current_page': counsel_page_obj.number,
                'counsel_total_pages': counsel_page_obj.paginator.num_pages,
            })
        if 'counselor_page' in request.GET:
            counselor_list = [
                {
                    'name': counselor.id.name,
                    'gender': '남자' if counselor.gender == 'M' else '여자',
                    'id': counselor.id.id,
                }
                for counselor in counselor_page_obj
            ]
            return JsonResponse({
                'counselors': counselor_list,
                'counselor_has_previous': counselor_page_obj.has_previous(),
                'counselor_has_next': counselor_page_obj.has_next(),
                'counselor_previous_page_number': counselor_page_obj.previous_page_number() if counselor_page_obj.has_previous() else None,
                'counselor_next_page_number': counselor_page_obj.next_page_number() if counselor_page_obj.has_next() else None,
                'counselor_current_page': counselor_page_obj.number,
                'counselor_total_pages': counselor_page_obj.paginator.num_pages,
            })

    return render(request, 'counsel/counsel_home.html', {
        'user': user,
        'counsels': counsels,
        'counselors': counselors,
        'counsel_page_obj': counsel_page_obj,
        'counselor_page_obj': counselor_page_obj,
    })

@login_required(redirect_field_name='login')
def counsel_apply(request):
    if request.method == 'POST':
        user = request.user
        counselor_id = request.POST.get('counselor_id')
        counsel_date = request.POST.get('counsel_date')
        counsel_content = request.POST.get('counsel_content')

        Counsel.objects.create(
            user_id=user.id,
            counselor_id=counselor_id,
            counsel_date=counsel_date,
            counsel_content=counsel_content,
        )
        messages.success(request, '상담이 성공적으로 신청되었습니다.')
    else:
        messages.error(request, "잘못된 요청입니다.")