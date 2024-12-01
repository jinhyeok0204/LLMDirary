from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from .forms import PostForm, PostCommentForm
from .models import Post


@login_required(redirect_field_name='login')
def community_home_view(request):
    posts = Post.objects.all().order_by('-post_write_datetime') # 작성일 기준 내림차순 정렬
    paginator = Paginator(posts, 10)  # 페이지당 10개 게시글
    page_number = request.GET.get('page')  # 현재 페이지 번호
    page_obj = paginator.get_page(page_number)  # 해당 페이지의 데이터

    context = {
        'page_obj': page_obj,
    }
    return render(request, "community/community_home.html", context)


@login_required(redirect_field_name='login')
def community_write_view(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.post_publisher = request.user
            post.save()
            return redirect('community_home')
    else:
        form = PostForm()

    context = {
        'form': form
    }
    return render(request, "community/community_write.html", context)


@login_required(redirect_field_name='login')
def community_detail_view(request, post_id):
    '''
    게시글 상세보기 화면
    - 게시글 내용과 댓글 표시 및 댓글 작성 기능.
    '''
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all().order_by('post_comment_write_datetime')

    if request.method == 'POST':
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
    }
    return render(request, "community/community_detail.html", context)

@login_required(redirect_field_name='login')
def post_delete_view(request, post_id):
    '''
    게시글 삭제 뷰
    - 로그인한 사용자가 게시글 작성자일 경우에만 삭제가능
    '''

    post = get_object_or_404(Post, pk=post_id)

    if post.post_publisher != request.user:
        return HttpResponseForbidden("이 게시글을 삭제할 권한이 없습니다.")

    if request.method == 'POST':
        post.delete()
        return redirect('community_home')