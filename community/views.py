from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from .forms import PostForm, PostCommentForm
from .models import Post, PostComment
from django.contrib import messages
from django.db.models import Count
from django.db import transaction


@login_required(redirect_field_name='login')
def community_home_view(request):
    posts = (
        Post.objects.annotate(comment_count=Count('comments'))
        .select_related('post_publisher')
        .order_by('-post_write_datetime')
    )

    # 검색 기능
    search_query = request.GET.get('search', '')
    if search_query:
        posts = posts.filter(post_publisher__login_id__icontains=search_query)

    # 정렬 기능: 댓글 수
    sort_by_comments = request.GET.get('sort_by_comments', '')
    if sort_by_comments == 'true':
        posts = posts.order_by('-comment_count', '-post_write_datetime')

    paginator = Paginator(posts, 5)  # 페이지당 5개 게시글
    page_number = request.GET.get('page')  # 현재 페이지 번호
    page_obj = paginator.get_page(page_number)  # 해당 페이지의 데이터

    is_admin_or_support = request.user.role in ['admin' or 'customer_support']

    context = {
        'page_obj': page_obj,
        'is_admin_or_support': is_admin_or_support,
        'search_query': search_query,
        'sort_by_comments': sort_by_comments,
    }
    return render(request, "community/community_home.html", context)


@login_required(redirect_field_name='login')
@transaction.atomic
def community_write_view(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.post_publisher = request.user

            if post.post_publisher.role in ['admin', 'customer_support']:
                post.is_pinned = True

            post.save()
            messages.success(request, '게시글이 작성되었습니다.')
            return redirect('community_home')
    else:
        form = PostForm()

    context = {
        'form': form
    }
    return render(request, "community/community_write.html", context)


@login_required(redirect_field_name='login')
@transaction.atomic
def community_detail_view(request, post_id):
    '''
    게시글 상세보기 화면
    - 게시글 내용과 댓글 표시 및 댓글 작성 기능.
    '''
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all().order_by('post_comment_write_datetime')

    role = request.user.role
    can_comment = role not in ['admin', 'customer_support']
    can_pin = role in ['admin', 'customer_support'] and post.post_publisher == request.user

    form = None
    if request.method == 'POST':
        if 'pin_post' in request.POST:
            # 공지 설정/해제
            if can_pin:
                post.is_pinned = not post.is_pinned
                post.save()
                status = "공지 등록" if post.is_pinned else "공지 해제"
                messages.success(request, f"게시글이 {status}되었습니다.")
            else:
                return HttpResponseForbidden("공지 설정 권한이 없습니다.")
        else:
            # 댓글 작성
            if not can_comment:
                return HttpResponseForbidden("댓글 작성 권한이 없습니다.")

            form = PostCommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.user = request.user.user
                comment.save()
            return redirect('community_detail', post_id=post.post_id)
    else:
        form = PostCommentForm()

    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'can_comment': can_comment,
        'can_pin': can_pin
    }
    return render(request, "community/community_detail.html", context)


@login_required(redirect_field_name='login')
@transaction.atomic
def post_delete_view(request, post_id):
    '''
    게시글 삭제 뷰
    - 로그인한 사용자가 게시글 작성자일 경우에만 삭제가능
    '''

    post = get_object_or_404(Post, pk=post_id)
    role = request.user.role
    if post.post_publisher != request.user and role not in ['customer_support', 'admin']:
        messages.error(request, "게시글 삭제 권한이 없습니다.")
        return HttpResponseForbidden("이 게시글을 삭제할 권한이 없습니다.")

    if request.method == 'POST':
        post.delete()
        messages.success(request, '게시글이 성공적으로 삭제되었습니다.')
        return redirect('community_home')


@login_required(redirect_field_name='login')
@transaction.atomic
def comment_delete_view(request, post_id, comment_id):
    '''
    댓글 삭제 뷰
    '''
    comment = get_object_or_404(PostComment, pk=comment_id, post__post_id=post_id)

    role = request.user.role
    if comment.user.id.id != request.user.id and role not in ['admin', 'customer_support']:
        messages.error(request, "댓글 삭제 권한이 없습니다.")
        return HttpResponseForbidden("댓글 삭제 권한이 없습니다.")
    else:
        comment.delete()
        messages.success(request, "댓글이 성공적으로 삭제되었습니다.")

    return redirect('community_detail', post_id=post_id)