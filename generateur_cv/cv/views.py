from django.shortcuts import render, redirect, get_object_or_404
from .models import CV
from django.contrib import messages

def accueil(request):
    return render(request, 'accueil.html')

def cv(request):
    if request.method == 'POST':
        cv = CV(
            nom=request.POST['nom'],
            email=request.POST['email'],
            telephone=request.POST['telephone'],
            experience=request.POST['experience'],
            formation=request.POST['formation'],
        )
        cv.save()
        messages.success(request, 'CV enregistré avec succès 😁')
        return redirect('admin:index')
    return render(request, 'cv.html')

def cv_detail(request, pk):
    cv = get_object_or_404(CV, pk=pk)
    return render(request, 'cv_detail.html', {'cv': cv})

def cv_list(request):
    cv_list = CV.objects.all()
    return render(request, 'cv_list.html', {'cv_list': cv_list})