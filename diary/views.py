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
import random

bertmodel = BertModel.from_pretrained('skt/kobert-base-v1', return_dict=False)
model = BERTClassifier(bertmodel, hidden_size=768, num_classes=6, dr_rate=0.5)
save_path = "./koBERT-emotion/bert_classifier_model.pt"
state_dict = torch.load(save_path, map_location=torch.device('cpu'))
model.load_state_dict(state_dict)
model.eval()
print("Model loaded successfully")
tokenizer = KoBERTTokenizer.from_pretrained('skt/kobert-base-v1')

emotions = ('anger', 'sadness', 'anxiety', 'hurt', 'embarrassment', 'happiness')

recommendations = {
    'anger': [
        "깊은 숨을 들이마시고 천천히 내쉬는 호흡 운동을 5분 동안 해보세요.",
        "화가 나는 원인을 적어보고, 그것을 해결할 수 있는 방법을 구체적으로 생각해 보세요.",
        "산책이나 조깅 같은 가벼운 신체 활동으로 마음을 진정시켜 보세요.",
        "화가 나는 순간에는 잠시 자리를 피하고 다른 일에 집중해 보세요.",
        "음악을 들으며 마음을 차분하게 만들어 보세요. 클래식이나 잔잔한 음악이 효과적일 수 있습니다."
    ],
    'sadness': [
        "믿을 수 있는 친구나 가족에게 자신의 감정을 솔직하게 털어놓아 보세요.",
        "따뜻한 차나 음료를 마시며 차분한 시간을 가져 보세요.",
        "좋아하는 영화를 보거나 책을 읽으며 긍정적인 에너지를 느껴 보세요.",
        "스스로를 격려하는 메시지를 적거나 긍정적인 문구를 읽어 보세요.",
        "실외로 나가 햇볕을 쬐며 산책을 하면 기분이 조금 나아질 수 있습니다."
    ],
    'anxiety': [
        "복식 호흡을 통해 긴장을 풀어 보세요. (4초 들이마시기, 6초 멈추기, 8초 내쉬기)",
        "불안한 원인을 적어보고, 실현 가능성과 해결 방안을 적어 보세요.",
        "요가나 명상을 통해 심신의 안정감을 찾아 보세요.",
        "'지금 이 순간'에 집중하며 작은 것에 감사하는 연습을 해보세요.",
        "손을 따뜻한 물에 담그고, 차분한 상태를 만들어 보세요."
    ],
    'hurt': [
        "자신에게 따뜻한 말을 건네며 스스로를 위로해 보세요.",
        "과거의 긍정적인 경험이나 좋은 기억을 떠올려 보세요.",
        "하루 동안 좋아하는 활동(요리, 그림 그리기 등)을 통해 자신을 돌봐 보세요.",
        "상처받은 원인을 적고, 시간이 지나면 무뎌질 수 있다는 것을 떠올려 보세요.",
        "마음을 달래주는 잔잔한 음악이나 자연 소리를 들어보세요."
    ],
    'embarrassment': [
        "당황한 순간을 적고, 그것이 심각하지 않음을 스스로에게 상기시켜 보세요.",
        "잠시 자리를 벗어나 심호흡을 하며 마음을 진정시켜 보세요.",
        "차분히 생각하며 '모두가 실수를 한다'는 사실을 받아들여 보세요.",
        "자신이 좋아하는 짧은 휴식을 취하며 머리를 맑게 만들어 보세요.",
        "같은 상황에서 대처할 다른 방법을 떠올려 보며 긍정적으로 생각해 보세요."
    ],
    'happiness': [
        "기쁜 순간을 일기에 자세히 기록하고, 미래에 다시 읽어보세요.",
        "기쁜 마음을 친구나 가족과 나누며 함께 즐거워 보세요.",
        "좋아하는 음악을 듣거나, 춤을 추며 기쁨을 더욱 만끽해 보세요.",
        "자신에게 작은 선물을 하며 기쁜 마음을 기념해 보세요.",
        "기쁨의 이유를 적고, 감사한 마음을 느껴 보세요."
    ]
}


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
            recommend_action = generate_recommendation(max_emotion)
            print(recommend_action)
            emotion_analysis = EmotionAnalysis.objects.create(
                anger_score=emotion_scores[0],
                sadness_score=emotion_scores[1],
                anxiety_score=emotion_scores[2],
                hurt_score=emotion_scores[3],
                embarrassment_score=emotion_scores[4],
                happiness_score=emotion_scores[5],
                summary = max_emotion,
                recommend_action=recommend_action
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


@login_required()
def diary_detail_view(request, diary_id):
    diary = get_object_or_404(Diary, pk=diary_id, user=request.user.user)
    emotion_analysis = diary.emotion_analysis

    total_score = sum([
        emotion_analysis.anger_score,
        emotion_analysis.sadness_score,
        emotion_analysis.anxiety_score,
        emotion_analysis.hurt_score,
        emotion_analysis.embarrassment_score,
        emotion_analysis.happiness_score
    ])

    # 감정 확률 계산
    if total_score > 0:
        emotion_percentages = {
            "분노": round((emotion_analysis.anger_score / total_score) * 100, 2),
            "슬픔": round((emotion_analysis.sadness_score / total_score) * 100, 2),
            "불안": round((emotion_analysis.anxiety_score / total_score) * 100, 2),
            "상처": round((emotion_analysis.hurt_score / total_score) * 100, 2),
            "당황": round((emotion_analysis.embarrassment_score / total_score) * 100, 2),
            "기쁨": round((emotion_analysis.happiness_score / total_score) * 100, 2),
        }
    else:
        emotion_percentages = {}

    context = {
        'diary': diary,
        'emotion_analysis': emotion_analysis,
        'emotion_percentages': emotion_percentages,  # 확률 정보 전달
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


def generate_recommendation(max_emotion):
    return random.choice(recommendations.get(max_emotion, ["추천 행동이 없습니다."]))