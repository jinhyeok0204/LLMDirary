from django.shortcuts import render

# Create your views here.

def community_home_view(request):
    if request.method == 'POST':
        pass
    return render("community/home.html")