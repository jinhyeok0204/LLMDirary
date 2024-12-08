from django.http import HttpResponseForbidden
from django.contrib import messages
from django.utils.timezone import now, timedelta
from accounts.models import Person, Counselor, CustomerSupport
from community.models import Post
from django.contrib.auth.decorators import login_required
from django.db import models, transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse


@login_required
def admin_home(request):
    person = Person.objects.get(id=request.user.id)
    if person.role != 'admin':
        messages.error(request, "관리자만 접근 가능합니다.")
        return HttpResponseForbidden("관리자만 접근 가능합니다.")

    pending_counselors = Counselor.objects.filter(is_approved=False)
    pending_supports = CustomerSupport.objects.filter(is_approved=False)

    admin_user = request.user
    one_month_ago = now() - timedelta(days=30)
    recent_posts = Post.objects.filter(post_publisher=admin_user, post_write_datetime__gte=one_month_ago)

    pinned_posts_count = Post.objects.filter(post_publisher=admin_user, is_pinned=True).count()
    recent_posts_count = recent_posts.count()

    supports = CustomerSupport.objects.all()
    avg_salary = supports.aggregate(models.Avg('salary'))['salary__avg'] if supports.exists() else 0
    max_salary = supports.aggregate(models.Max('salary'))['salary__max'] if supports.exists() else 0
    min_salary = supports.aggregate(models.Min('salary'))['salary__min'] if supports.exists() else 0

    context = {
        'pending_counselors': pending_counselors,
        'pending_supports': pending_supports,
        'recent_posts_count': recent_posts_count,
        'pinned_posts_count': pinned_posts_count,
        'avg_salary': avg_salary,
        'max_salary': max_salary,
        'min_salary': min_salary,
    }

    return render(request, 'admin/admin_home.html', context)


@login_required()
def admin_join_requests(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("관리자만 접근할 수 있습니다.")

    counselor_requests = Counselor.objects.filter(is_approved=False)
    support_requests = CustomerSupport.objects.filter(is_approved=False)

    context = {
        'counselor_requests': counselor_requests,
        'support_requests': support_requests,
    }
    return render(request, 'admin/admin_join_requests.html', context)


@login_required()
@transaction.atomic
def update_request_status(request, role, person_id, action):
    if role == 'counselor':
        person = get_object_or_404(Counselor, id=person_id)
    elif role == 'customer_support':
        person = get_object_or_404(CustomerSupport, id=person_id)
    else:
        return JsonResponse({'success':'False', 'message': 'Invalid role'})

    if action == 'approve':
        person.is_approved = True
    elif action == 'reject':
        person.is_approved = False
    else:
        return JsonResponse({'success':'False', 'message': 'Invalid action'})

    person.save()
    return JsonResponse({'success':'True'})


@login_required()
def admin_activity_logs(request):

    return None


@login_required()
def admin_salary_management(request):
    if request.user.role != 'admin':
        return HttpResponseForbidden("권한이 없습니다.")

        # 검색 및 필터링
    query = request.GET.get('query', '')
    min_salary = request.GET.get('min_salary', None)
    max_salary = request.GET.get('max_salary', None)

    supports = CustomerSupport.objects.all()

    if query:
        supports = supports.filter(id__name__icontains=query)
    if min_salary:
        supports = supports.filter(salary__gte=min_salary)
    if max_salary:
        supports = supports.filter(salary__lte=max_salary)

    # 급여 정렬
    sort_by_salary = request.GET.get('sort_by_salary', None)
    if sort_by_salary == 'asc':
        supports = supports.order_by('salary')
    elif sort_by_salary == 'desc':
        supports = supports.order_by('-salary')

    context = {
        'supports': supports,
    }
    return render(request, 'admin/admin_salary_management.html', context)


@login_required()
@transaction.atomic
def admin_update_salary(request, support_id):
    if request.user.role != 'admin':
        return HttpResponseForbidden("권한이 업습니다.")

    support = get_object_or_404(CustomerSupport, id=support_id)

    if request.method == "POST":
        new_salary = request.POST.get("new_salary", None)
        try:
            new_salary = int(new_salary)
            if new_salary < 0:
                raise ValueError("급여는 음수일 수 없습니다.")

            support.salary = new_salary
            support.save()
            messages.success(request, f"{support.id.name}의 급여가 업데이트되었습니다.")
        except ValueError as e:
            messages.error(request, f"급여 업데이트 실패: {e}")
    return redirect('admin_salary_management')