from django.shortcuts import render, redirect, get_object_or_404
from .models import CV
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django_otp.decorators import otp_required

def accueil(request):
    return render(request, 'accueil.html')

@login_required
@otp_required
def cv(request):
    if request.method == 'POST':
        cv = CV(
            nom=request.POST['nom'],
            prenom=request.POST.get('prenom', ''),  # Add prenom field support
            email=request.POST['email'],
            telephone=request.POST['telephone'],
            experience=request.POST['experience'],
            formation=request.POST['formation'],
        )
        cv.save()
        messages.success(request, 'CV enregistré avec succès 😁')
        return redirect('cv_list')
    return render(request, 'cv.html')

@login_required
@otp_required
def cv_detail(request, pk):
    cv = get_object_or_404(CV, pk=pk)
    return render(request, 'cv_detail.html', {'cv': cv})

@login_required
@otp_required
def cv_list(request):
    cv_list = CV.objects.all()
    return render(request, 'cv_list.html', {'cv_list': cv_list})