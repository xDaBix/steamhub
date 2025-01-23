from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from developers.models import Game

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('is_admin_logged_in'):
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            request.session['is_admin_logged_in'] = True
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid credentials. Please try again.")

    return render(request, 'hubadmin/admin_login.html')

def admin_logout(request):
    request.session.flush()
    return redirect('admin_login')

@admin_required
def admin_dashboard(request):
    pending_games = Game.objects.filter(status='pending')
    return render(request, 'hubadmin/admin_dashboard.html', {'pending_games': pending_games})

@admin_required
def approve_game(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    game.status = 'approved'
    game.save()
    messages.success(request, f"{game.title} has been approved.")
    return redirect('admin_dashboard')

@admin_required
def reject_game(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    game.status = 'rejected'
    game.save()
    messages.success(request, f"{game.title} has been rejected.")
    return redirect('admin_dashboard')

@admin_required
def approved_games(request):
    approved_games = Game.objects.filter(status='approved')
    return render(request, 'hubadmin/approved_games.html', {'approved_games': approved_games})

@admin_required
def rejected_games(request):
    rejected_games = Game.objects.filter(status='rejected')
    return render(request, 'hubadmin/rejected_games.html', {'rejected_games': rejected_games})
