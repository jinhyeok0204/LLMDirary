from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.timezone import now
from accounts.models import Counselor


@login_required(redirect_field_name='login')
def counsel_home(request):
    user = request.user
    counselors = Counselor.objects.filter(is_approved=True).select_related('id')

    return render(request, 'counsel/counsel_home.html', {
        'user': user,
        'counselors': counselors,
    })

@login_required(redirect_field_name='login')
def counsel_apply(request):
    user = request.user

    if request.method == 'POST':
        counselor_id = request.POST.get('counselor_id')
        appointment_date = request.POST.get('appointment_date')  # 상담 날짜

        # 상담사 유효성 검사
        counselor = get_object_or_404(Counselor.objects.filter(is_approved=True).select_related('id'), pk=counselor_id)

        if not appointment_date:
            return HttpResponse("예약 날짜를 선택해주세요.", status=400)

        # 상담 예약 처리 (추가적으로 상담 예약 모델 필요)
        # 예시 코드: CounselSchedule 모델이 있다고 가정
        # CounselSchedule.objects.create(
        #     user=user,
        #     counselor=counselor,
        #     appointment_date=appointment_date,
        #     created_at=now()
        # )

        # 예약 완료 후 홈으로 리다이렉트
        return redirect('counsel')
