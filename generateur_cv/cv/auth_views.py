from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django_otp.decorators import otp_required
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp import user_has_device
import qrcode
import io
import base64
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm, TwoFactorTokenForm


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Compte créé avec succès! Vous pouvez maintenant vous connecter.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user has 2FA enabled
            if user_has_device(user):
                # Store user in session for 2FA verification
                request.session['pre_2fa_user_id'] = user.id
                return redirect('two_factor_verify')
            else:
                # Log in directly if no 2FA
                login(request, user)
                messages.success(request, 'Connexion réussie!')
                return redirect('/')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})


@login_required
def setup_2fa_view(request):
    user = request.user
    device = None
    
    # Check if user already has a TOTP device
    try:
        device = TOTPDevice.objects.get(user=user, confirmed=True)
    except TOTPDevice.DoesNotExist:
        # Create new device if none exists
        device = TOTPDevice.objects.create(
            user=user,
            name='default',
            confirmed=False
        )
    
    if request.method == 'POST':
        token_form = TwoFactorTokenForm(request.POST)
        if token_form.is_valid():
            token = token_form.cleaned_data['token']
            # Verify the token
            if device.verify_token(token):
                device.confirmed = True
                device.save()
                messages.success(request, 'Authentification à deux facteurs activée avec succès!')
                return redirect('profile')
            else:
                messages.error(request, 'Code invalide. Veuillez réessayer.')
    else:
        token_form = TwoFactorTokenForm()
    
    # Generate QR code
    qr_code_url = device.config_url
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_code_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    context = {
        'qr_code_base64': qr_code_base64,
        'secret_key': device.key,
        'token_form': token_form,
        'device_confirmed': device.confirmed
    }
    
    return render(request, 'registration/setup_2fa.html', context)


def two_factor_verify_view(request):
    user_id = request.session.get('pre_2fa_user_id')
    if not user_id:
        return redirect('login')
    
    try:
        from django.contrib.auth.models import User
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('login')
    
    if request.method == 'POST':
        token_form = TwoFactorTokenForm(request.POST)
        if token_form.is_valid():
            token = token_form.cleaned_data['token']
            
            # Check TOTP devices
            devices = TOTPDevice.objects.filter(user=user, confirmed=True)
            for device in devices:
                if device.verify_token(token):
                    # Clean up session
                    del request.session['pre_2fa_user_id']
                    # Login user
                    login(request, user)
                    messages.success(request, 'Connexion réussie avec authentification à deux facteurs!')
                    return redirect('/')
            
            messages.error(request, 'Code invalide. Veuillez réessayer.')
    else:
        token_form = TwoFactorTokenForm()
    
    return render(request, 'registration/two_factor_verify.html', {'token_form': token_form})


@login_required
def profile_view(request):
    user = request.user
    has_2fa = user_has_device(user)
    devices = TOTPDevice.objects.filter(user=user, confirmed=True)
    
    context = {
        'user': user,
        'has_2fa': has_2fa,
        'devices': devices
    }
    
    return render(request, 'registration/profile.html', context)


@login_required
def disable_2fa_view(request):
    if request.method == 'POST':
        # Delete all TOTP devices for the user
        TOTPDevice.objects.filter(user=request.user).delete()
        messages.success(request, 'Authentification à deux facteurs désactivée.')
        return redirect('profile')
    
    return render(request, 'registration/disable_2fa.html')