from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.timezone import now
from accounts.models import Counselor
from .models import Counsel
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.core.paginator import EmptyPage

@login_required(redirect_field_name='login')
def counsel_home(request):
    user = request.user
    counsels = Counsel.objects.filter(user=user.id).select_related('counselor').order_by('counsel_id')
    counselors = Counselor.objects.filter(is_approved=True).select_related('id').order_by('id__name')

    # 페이지네이션 설정
    paginator = Paginator(counselors, 3)  # 페이지당 상담사 3명
    page_number = request.GET.get('page', 1)  # 페이지 번호 기본값을 1로 설정

    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        page_obj = paginator.get_page(1)  # 빈 페이지 요청 시 첫 페이지로 설정

    # AJAX 요청인지 확인
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        counselor_list = [
            {
                'name': counselor.id.name,
                'gender': '남자' if counselor.gender == 'M' else '여자',
                'id': counselor.id.id,
            }
            for counselor in page_obj
        ]
        return JsonResponse({
            'counselors': counselor_list,
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
            'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
            'current_page': page_obj.number,
            'total_pages': page_obj.paginator.num_pages,
        })

    return render(request, 'counsel/counsel_home.html', {
        'user': user,
        'counsels': counsels,
        'counselors': counselors,
        'page_obj': page_obj,
    })

@login_required(redirect_field_name='login')
def counsel_apply(request):
    if request.method == 'POST':
        user = request.user
        counselor_id = request.POST.get('counselor_id')
        counsel_date = request.POST.get('counsel_date')
        counsel_content = request.POST.get('counsel_content')

        counselor = get_object_or_404(Counselor, id=counselor_id)

        Counsel.objects.create(
            user=user,
            counselor=counselor,
            counsel_date=counsel_date,
            content=counsel_content,
        )
        return JsonResponse({'message': '상담 신청이 완료되었습니다.'})
    return JsonResponse({'error': '잘못된 요청입니다.'}, status=400)