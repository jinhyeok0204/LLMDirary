from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Diary, EmotionAnalysis
from .forms import DiaryForm
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.urls import reverse
import json
from .classifier_model import BERTClassifier
import torch
from transformers import BertModel
from kobert_tokenizer import KoBERTTokenizer

bertmodel = BertModel.from_pretrained('skt/kobert-base-v1', return_dict=False)
model = BERTClassifier(bertmodel, hidden_size=768, num_classes=6, dr_rate=0.5)
save_path = "./koBERT-emotion/bert_classifier_model.pt"
state_dict = torch.load(save_path, map_location=torch.device('cpu'))
model.load_state_dict(state_dict)
model.eval()
print("Model loaded successfully")
tokenizer = KoBERTTokenizer.from_pretrained('skt/kobert-base-v1')

emotions = ('anger', 'sadness', 'anxiety', 'hurt', 'embarrassment', 'happiness')


@login_required(redirect_field_name='login')
@transaction.atomic
def diary_write_view(request):
    if request.method == 'POST':
        form = DiaryForm(request.POST)
        if form.is_valid():
            diary_date = form.cleaned_data['diary_date']
            # 중복 검사
            if Diary.objects.filter(user=request.user.user, diary_date=diary_date).exists():
                messages.error(request, f"{diary_date}에 이미 작성된 일기가 있습니다.")
                return render(request, "diary/diary_write.html", {'form': form})
            diary = form.save(commit=False)
            diary.user = request.user.user

            content = form.cleaned_data['content']
            emotion_scores = predict_emotion(content)

            max_emotion_idx = emotion_scores.index(max(emotion_scores))
            max_emotion = emotions[max_emotion_idx]

            emotion_analysis = EmotionAnalysis.objects.create(
                anger_score=emotion_scores[0],
                sadness_score=emotion_scores[1],
                anxiety_score=emotion_scores[2],
                hurt_score=emotion_scores[3],
                embarrassment_score=emotion_scores[4],
                happiness_score=emotion_scores[5],
                summary = max_emotion,
                recommend_action="기본 추천"
            )
            # Diary와 EmotgionAnalysis 연결
            diary.emotion_analysis = emotion_analysis
            diary.save()
            messages.success(request, '일기가 성공적으로 저장되었습니다.')
            return redirect('diary')
        else:
            messages.error(request, '일기 저장에 실패했습니다.')
    else:
        form = DiaryForm()
    return render(request, 'diary/diary_write.html', {'form': form})


@login_required()
def diary_home_view(request):
    diaries = Diary.objects.filter(user=request.user.user).order_by('-diary_date')
    paginator = Paginator(diaries, 10)  # 페이지당 10개 게시글
    page_number = request.GET.get('page')  # 현재 페이지 번호
    page_obj = paginator.get_page(page_number)  # 해당 페이지의 데이터

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'diary/diary_home.html', context)


@login_required()
@transaction.atomic
def diary_edit_view(request, diary_id):
    '''
    다이어리 수정 뷰
    '''
    diary = get_object_or_404(Diary, pk=diary_id, user=request.user.user)

    if request.method == 'POST':
        form = DiaryForm(request.POST, instance=diary)
        if form.is_valid():
            form.save()
            messages.success(request, '일기가 성공적으로 수정되었습니다.')
            return redirect('diary_detail', diary_id=diary.diary_id)
        else:
            print("폼 검증 실페:", form.errors)
            print(form)
            messages.error(request, '일기 수정에 실패했습니다.')
    else:
        form = DiaryForm(instance=diary)
    context = {
        'form': form,
        'diary': diary,
    }
    return render(request, 'diary/diary_edit.html', context)


@login_required()
@require_POST
@transaction.atomic
def diary_delete_view(request):
    '''
    특정 다이어리 삭제하는 뷰
    '''
    data = json.loads(request.body)
    diary_id = data.get('diary_id')

    if not diary_id:
        return JsonResponse({'success': False, 'message': 'Diary Id is required.'})

    diary = get_object_or_404(Diary, pk=diary_id, user = request.user.user)

    diary.delete()

    messages.success(request, "일기가 성공적으로 삭제되었습니다.")
    return JsonResponse({
        'success': True,
        'redirect_url': reverse('diary'),
    })


def diary_detail_view(request, diary_id):
    diary = get_object_or_404(Diary, pk=diary_id, user=request.user.user)
    context = {
        'diary' : diary,
    }
    return render(request, 'diary/diary_detail.html', context)


def predict_emotion(content):
    inputs = tokenizer(content, return_tensors='pt', padding=True, max_length=256)
    token_ids = inputs['input_ids']
    attention_mask = inputs['attention_mask']
    token_type_ids = inputs['token_type_ids']

    with torch.no_grad():
        output = model(token_ids, attention_mask.sum(dim=1), token_type_ids)

    probabilities = torch.nn.functional.softmax(output, dim=1).squeeze().tolist()
    scores = [round(prob * 10, 2) for prob in probabilities]
    return scores

