from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from .models import LoginHistory
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.db.models import Max

def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'tracking_users/home.html')

def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            LoginHistory.objects.create(
                user=user,
                login_time=timezone.now()
            )
            return redirect('home')
        else:
            return render(request, 'tracking_users/login.html', {'error': 'Identifiants incorrects.'})
    return render(request, 'tracking_users/login.html')

def user_logout(request):
    if request.user.is_authenticated:
        last_login = LoginHistory.objects.filter(
            user=request.user, logout_time__isnull=True
        ).last()

        if last_login and last_login.login_time:
            last_login.logout_time = timezone.now()
            last_login.session_duration = last_login.logout_time - last_login.login_time
            last_login.save()

    logout(request)
    return redirect('login')

def login_history(request):
    if not request.user.is_staff:
        return redirect('home')
    
    latest_logins = (
        LoginHistory.objects
        .values('user')
        .annotate(latest_login=Max('login_time'))
    )

    latest_entries = LoginHistory.objects.filter(
        login_time__in=[item['latest_login'] for item in latest_logins]
    ).select_related('user').order_by('user__username')

    return render(request, 'tracking_users/login_history.html', {'history': latest_entries})

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        errors = []
        if password1 != password2:
            errors.append("Les mots de passe ne correspondent pas.")
        if User.objects.filter(username=username).exists():
            errors.append("Ce nom d'utilisateur est déjà pris.")
        if User.objects.filter(email=email).exists():
            errors.append("Cet email est déjà utilisé.")

        if errors:
            return render(request, 'tracking_users/register.html', {'errors': errors})
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            login(request, user)
            return redirect('home')
    return render(request, 'tracking_users/register.html')

def activate_user(request, user_id):
    if not request.user.is_staff:
        return redirect('home')

    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f"L'utilisateur {user.username} a été activé avec succès .")
    return redirect('login_history')


def deactivate_user(request, user_id):
    if not request.user.is_staff:
        return redirect('home')

    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.warning(request, "Vous ne pouvez pas vous désactiver vous-même .")
        return redirect('login_history')

    user.is_active = False
    user.save()
    messages.warning(request, f"L'utilisateur {user.username} a été désactivé .")
    return redirect('login_history')