from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from .models import LoginHistory

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

    history = LoginHistory.objects.select_related('user').order_by('-login_time')
    return render(request, 'tracking_users/login_history.html', {'history': history})

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