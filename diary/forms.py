from django import forms
from .models import Diary


class DiaryForm(forms.ModelForm):
    class Meta:
        model = Diary
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-lg',
                'placeholder': '제목을 입력하세요',
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full p-4 border border-gray-300 rounded-lg',
                'placeholder': '내용을 작성하세요...',
                'rows': 6,
            }),
        }
        labels = {
            'title': '제목',
            'content': '내용',
        }