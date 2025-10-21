from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib import messages
from django.db.models import Max
from .models import LoginHistory
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'tracking_users/home.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            login_record = LoginHistory.objects.create(
                user=user,
                login_time=timezone.now()
            )
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "admin_notifications",
                {
                    "type": "user_event",
                    "user": user.username,
                    "login_time": login_record.login_time.isoformat(),
                }
            )

            return redirect('home')
        else:
            return render(request, 'tracking_users/login.html', {'error': 'Identifiants incorrects'})

    return render(request, 'tracking_users/login.html')

def user_logout(request):
    if request.user.is_authenticated:
        last_login = LoginHistory.objects.filter(
            user=request.user,
            logout_time__isnull=True
        ).last()

        if last_login and last_login.login_time:
            last_login.logout_time = timezone.now()
            last_login.session_duration = last_login.logout_time - last_login.login_time
            last_login.save()
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "admin_notifications",
                {
                    "type": "user_event",
                    "user": request.user.username,
                    "logout_time": last_login.logout_time.isoformat(),
                    "session_duration": str(last_login.session_duration),
                }
            )

        logout(request)
        return redirect('login')

def login_history(request):
    if not request.user.is_staff:
        return redirect('home')

    last_logins = (
        LoginHistory.objects
        .values('user')
        .annotate(last_login=Max('login_time'))
    )

    latest_entries = (
        LoginHistory.objects
        .filter(login_time__in=[item['last_login'] for item in last_logins])
        .select_related('user')
        .order_by('-login_time')
    )

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
    messages.success(request, f"L'utilisateur {user.username} a été activé avec succès.")
    return redirect('login_history')

def deactivate_user(request, user_id):
    if not request.user.is_staff:
        return redirect('home')

    user = get_object_or_404(User, id=user_id)
    if user_id == request.user.id :
        messages.error(request, "Vous ne pouvez pas vous désactiver vous même!")
        return redirect('login_history')
    
    user.is_active = False
    user.save()
    messages.warning(request, f"L'utilisateur {user.username} a été désactivé.")
    return redirect('login_history')