from django import forms
from .models import Post, PostComment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['post_title', 'post_content']  # 사용자가 입력할 필드
        widgets = {
            'post_title' : forms.TextInput(attrs={
                'class': "w-full p-2 border border-gray-300 rounded-lg",
                'placeholder' : 'Enter the post title',
            }),

            'post_content': forms.Textarea(attrs={
                'class': 'w-full p-4 border border-gray-300 rounded-lg',
                'placeholder': 'Write your post here...',
                'rows': 6,
            }),
        }
        labels = {
            'post_title': '제목',
            'post_content': '내용',
        }


class PostCommentForm(forms.ModelForm):
    class Meta:
        model = PostComment
        fields = ['post_comment_content']
        widgets = {
            'post_comment_content': forms.Textarea(attrs={
                'class': 'w-full p-4 border border-gray-300 rounded-lg',
                'placeholder': 'Write your comment here...',
                'rows': 3,
            }),
        }
        labels = {
            'post_comment_content': '댓글 내용',
        }
