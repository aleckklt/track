from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .models import LoginHistory
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.utils.timezone import now
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session['connected_at'] = str(now())

            log = LoginHistory.objects.create(user=user, connected_at=now())
            request.session['log_id'] = log.id
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "admin_notifications",
                {
                    "type": "user_connected",
                    "data": {
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "email": user.email,
                        "connected_at": str(log.login_time)
                    }
                }
            )
            return redirect("home")
    return render(request, "tracking_users/home.html")

def logout_view(request):
    logout(request)
    return redirect("login")

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

@staff_member_required
def login_history(request):
    history = LoginHistory.objects.all().select_related('user').order_by('-login_time')
    return render(request, 'tracking_users/login_history.html', {'history': history})

def home(request):
    return render(request, 'tracking_users/home.html')
