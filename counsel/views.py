from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.timezone import now, make_aware, get_current_timezone
from accounts.models import Counselor
from .models import Counsel
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.core.paginator import EmptyPage
from django.contrib import messages

@login_required(redirect_field_name='login')
def counsel_home(request):
    user = request.user
    counsels = Counsel.objects.filter(user=user.id).select_related('counselor').order_by('-counsel_datetime')
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
                    'counsel_id': counsel.counsel_id,
                    'counselor_name': counsel.counselor.id.name,
                    'counsel_datetime': counsel.counsel_datetime,
                    'counsel_is_appointment': counsel.is_appointment,
                    'counsel_is_complete': counsel.is_complete,
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
        counsel_hour = request.POST.get('counsel_hour')
        counsel_minute = request.POST.get('counsel_minute')
        counsel_content = request.POST.get('counsel_content')

        # naive datetime 생성
        naive_datetime = datetime.strptime(
            f"{counsel_date} {counsel_hour}:{counsel_minute}", "%Y-%m-%d %H:%M"
        )

        # 시간대 인식 datetime으로 변환
        counsel_datetime = make_aware(naive_datetime)

        # 중복 예약 검사
        existing_counsel = Counsel.objects.filter(
            counselor_id=counselor_id,
            counsel_datetime=counsel_datetime
        ).exists()
        if existing_counsel:
            messages.error(request, "해당 시간에 이미 예약이 존재합니다.")
            return JsonResponse({'success': False, 'message': '해당 시간에 이미 예약이 존재합니다.'}, status=400)

        Counsel.objects.create(
            user_id=user.id,
            counselor_id=counselor_id,
            counsel_datetime=counsel_datetime,
            counsel_content=counsel_content,
        )
        messages.success(request, '상담이 성공적으로 신청되었습니다.')
        return JsonResponse({'success': True})
    else:
        messages.error(request, "잘못된 요청입니다.")
        return JsonResponse({'success': False}, status=400)

@login_required(redirect_field_name='login')
def counsel_detail(request):
    counsel_id = request.GET.get('counsel_id')
    counsel = get_object_or_404(Counsel, pk=counsel_id)
    return JsonResponse({
        'counselor_name': counsel.counselor.id.name,
        'counsel_datetime': counsel.counsel_datetime,
        'counsel_content': counsel.counsel_content,
        'counsel_is_appointment': counsel.is_appointment,
        'counsel_is_complete': counsel.is_complete,
    })

@login_required(redirect_field_name='login')
def cancel_reservation(request):
    if request.method == 'POST':
        counsel_id = request.POST.get('counsel_id')
        counsel = get_object_or_404(Counsel, pk=counsel_id)
        counsel.delete()  # 예약 삭제
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)
