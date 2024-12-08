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
from django.db.models import Q

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
                    'counselor_phone_number': counsel.counselor.id.phone_num,
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
                    'phone_num': counselor.id.phone_num,
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
        'counsel_counselor_gender': counsel.counselor.gender,
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

@login_required(redirect_field_name='login')
def counselor_counsel(request):
    user = request.user

    # 상담 내역: counselor_id가 본인이고 상담이 완료된 항목
    completed_counsels = Counsel.objects.filter(
        Q(counselor_id=user.id) & (Q(is_complete=True) | Q(is_appointment=True))
    ).order_by('-counsel_datetime')

    # 상담 대기 목록: counselor_id가 본인이고 is_appointment가 False인 항목
    pending_counsels = Counsel.objects.filter(
        counselor_id=user.id,
        is_appointment=False
    ).order_by('counsel_datetime')

    # 페이지네이션 설정
    completed_counsel_paginator = Paginator(completed_counsels, 3)
    completed_page_number = request.GET.get('completed_page', 1)
    try:
        completed_page_obj = completed_counsel_paginator.get_page(completed_page_number)
    except EmptyPage:
        completed_page_obj = completed_counsel_paginator.get_page(1)

    pending_counsel_paginator = Paginator(pending_counsels, 3)
    pending_page_number = request.GET.get('pending_page', 1)
    try:
        pending_page_obj = pending_counsel_paginator.get_page(pending_page_number)
    except EmptyPage:
        pending_page_obj = pending_counsel_paginator.get_page(1)

    # AJAX 요청인지 확인
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if 'completed_page' in request.GET:
            completed_list = [
                {
                    'counsel_id': counsel.counsel_id,
                    'user_name': counsel.user.id.name,
                    'user_gender': counsel.user.gender,
                    'counsel_datetime': counsel.counsel_datetime,
                    'counsel_content': counsel.counsel_content,
                    'counsel_complete': counsel.is_complete,
                }
                for counsel in completed_page_obj
            ]
            return JsonResponse({
                'completed_counsels': completed_list,
                'completed_has_previous': completed_page_obj.has_previous(),
                'completed_has_next': completed_page_obj.has_next(),
                'completed_previous_page_number': completed_page_obj.previous_page_number() if completed_page_obj.has_previous() else None,
                'completed_next_page_number': completed_page_obj.next_page_number() if completed_page_obj.has_next() else None,
                'completed_current_page': completed_page_obj.number,
                'completed_total_pages': completed_page_obj.paginator.num_pages,
            })
        if 'pending_page' in request.GET:
            pending_list = [
                {
                    'counsel_id': counsel.counsel_id,
                    'user_name': counsel.user.id.name,
                    'user_gender': counsel.user.gender,
                    'counsel_datetime': counsel.counsel_datetime,
                    'counsel_content': counsel.counsel_content,
                }
                for counsel in pending_page_obj
            ]
            return JsonResponse({
                'pending_counsels': pending_list,
                'pending_has_previous': pending_page_obj.has_previous(),
                'pending_has_next': pending_page_obj.has_next(),
                'pending_previous_page_number': pending_page_obj.previous_page_number() if pending_page_obj.has_previous() else None,
                'pending_next_page_number': pending_page_obj.next_page_number() if pending_page_obj.has_next() else None,
                'pending_current_page': pending_page_obj.number,
                'pending_total_pages': pending_page_obj.paginator.num_pages,
            })

    return render(request, 'counsel/counselor_counsel.html', {
        'completed_page_obj': completed_page_obj,
        'pending_page_obj': pending_page_obj,
    })

@login_required(redirect_field_name='login')
def accept_counsel(request):
    if request.method == 'POST':
        counsel_id = request.POST.get('counsel_id')
        counsel = get_object_or_404(Counsel, pk=counsel_id)

        # 상담 수락 처리
        counsel.is_appointment = True
        counsel.save()
        messages.success(request, '상담을 수락했습니다.')
        return JsonResponse({'success': True})
    messages.error(request, '상담 수락에 실패했습니다.')
    return JsonResponse({'success': False}, status=400)


@login_required(redirect_field_name='login')
def reject_counsel(request):
    if request.method == 'POST':
        counsel_id = request.POST.get('counsel_id')
        counsel = get_object_or_404(Counsel, pk=counsel_id)

        # 상담 거절 처리 (삭제 또는 다른 필드 수정)
        counsel.delete()
        messages.error(request, '상담을 거절했습니다.')
        return JsonResponse({'success': True})
    messages.error(request, '상담 거절에 실패했습니다.')
    return JsonResponse({'success': False}, status=400)

@login_required(redirect_field_name='login')
def complete_counsel(request):
    if request.method == 'POST':
        counsel_id = request.POST.get('counsel_id')
        counsel = get_object_or_404(Counsel, pk=counsel_id)

        counsel.is_complete = True
        counsel.save()
        messages.success(request, '상담을 완료했습니다.')
        return JsonResponse({'success': True})
    messages.error(request, '상담 완료에 실패했습니다.')
    return JsonResponse({'success': False}, status=400)

@login_required(redirect_field_name='login')
def change_counsel_date(request):
    if request.method == 'POST':
        counsel_id = request.POST.get('counsel_id')
        counsel_date = request.POST.get('new_counsel_date')
        counsel_hour = request.POST.get('new_counsel_hour')
        counsel_minute = request.POST.get('new_counsel_minute')

        # naive datetime 생성
        naive_datetime = datetime.strptime(
            f"{counsel_date} {counsel_hour}:{counsel_minute}", "%Y-%m-%d %H:%M"
        )

        # 시간대 인식 datetime으로 변환
        new_counsel_date = make_aware(naive_datetime)

        counsel = Counsel.objects.get(pk=counsel_id)
        counsel.counsel_datetime = new_counsel_date
        counsel.save()
        messages.success(request, '일정 변경을 완료했습니다.')
        return JsonResponse({'status': 'success'})
    messages.error(request, '일정 변경에 실패했습니다.')
    return JsonResponse({'status': 'error', 'message': '잘못된 요청입니다.'})