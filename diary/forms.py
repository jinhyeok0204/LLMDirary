from django import forms
from .models import Diary


class DiaryForm(forms.ModelForm):
    class Meta:
        model = Diary
        fields = ['diary_date', 'title', 'content']
        widgets = {
            'diary_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),

            'title': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-lg',
                'placeholder': '제목을 입력하세요',
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full p-4 border border-gray-300 rounded-lg',
                'placeholder': '',
                'rows': 6,
            }),
        }
        labels = {
            'diary_date': '날짜',
            'title': '제목',
            'content': '내용',
        }