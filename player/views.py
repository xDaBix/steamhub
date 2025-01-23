import json
import random
import re
from datetime import datetime
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from developers.models import Game
from itertools import groupby
from operator import itemgetter
from .forms import Registration
from .models import players
import razorpay
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect,get_list_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Payment,Library
from django.utils import timezone
from developers.models import Game
from django.http import HttpResponseForbidden
import os
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import logging
from datetime import timedelta
import razorpay
from .models import Payment, Library
from developers.models import Game

from player import models

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages  
from .models import Friendship, players
from django.contrib.auth.decorators import login_required


logger = logging.getLogger(__name__)

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

def signup(request):
    if request.method == "POST":
        form = Registration(request.POST)
        if form.is_valid():
            firstname = form.cleaned_data.get('firstname')
            lastname = form.cleaned_data.get('lastname')
            contactno = form.cleaned_data.get('contactno')
            gender = form.cleaned_data.get('gender')
            date_of_birth = form.cleaned_data.get('date_of_birth')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            
            email_exists = players.objects.filter(email=email).exists()
            username_exists = players.objects.filter(username=username).exists()

            if email_exists or username_exists:
                messages.error(request, 'Email or Username already exists.')
                return render(request, 'player/signup.html', {'form': form})

            otp = random.randint(10000, 99999)
            send_mail(
                'Your OTP Code',
                f'Your OTP code is {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            form.cleaned_data['date_of_birth'] = date_of_birth.strftime('%Y-%m-%d')
            form.cleaned_data['otp'] = otp

            request.session['registration_data'] = form.cleaned_data
            return redirect('verifyotp')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = Registration()

    return render(request, 'player/signup.html', {'form': form})


def home(request):
    is_logged_in = 'pid' in request.session
    games = Game.objects.all()  
    return render(request, 'player/home.html', {'games': games, 'is_logged_in': is_logged_in})



def check_user_exists(request):
    if request.method == "GET":
        email = request.GET.get('email', None)
        username = request.GET.get('username', None)

        email_exists = players.objects.filter(email=email).exists() if email else False
        username_exists = players.objects.filter(username=username).exists() if username else False

        message = None
        if email_exists and username_exists:
            message = "Email and username are already registered."
        elif email_exists:
            message = "Email is already registered."
        elif username_exists:
            message = "Username is already taken."

        response = {
            'email_exists': email_exists,
            'username_exists': username_exists,
            'message': message
        }

        return JsonResponse(response)



def verify_otp(request):
    if request.method == "POST":
        otp = request.POST.get('otp')
        registration_data = request.session.get('registration_data')

        if otp and registration_data and int(otp) == registration_data.get('otp'):
            date_of_birth_str = registration_data.get('date_of_birth')
            date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()

            user = players(
                first_name=registration_data.get('firstname'),
                last_name=registration_data.get('lastname'),
                username=registration_data.get('username'),
                email=registration_data.get('email'),
                password=make_password(registration_data.get('password')),
                contact=registration_data.get('contactno'),
                date_of_birth=date_of_birth,
                status='active'
            )
            user.save()

            request.session['pid'] = user.Players_id

            del request.session['registration_data']

            messages.success(request, 'Registration successful!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'player/verify_otp.html')


def login(request):
    user = None  
    
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = players.objects.get(email=email)
        except players.DoesNotExist:
            user = None

        if user:
            
            if user.lockout_time and timezone.now() >= user.lockout_time:
                user.lockout_time = None
                user.failed_attempts = 0
                user.save()

            
            if user.lockout_time and timezone.now() < user.lockout_time:
                messages.error(request, 'Your account is locked. Try again later.')
                return render(request, 'player/login.html', {'attempts_left': 0})

            
            if check_password(password, user.password):
                user.failed_attempts = 0
                user.lockout_time = None
                user.save()

                request.session['pid'] = user.Players_id
                return redirect('home')
            else:
                user.failed_attempts += 1

                if user.failed_attempts >= 3:
                    user.lockout_time = timezone.now() + timedelta(minutes=15)
                    messages.error(request, 'You have made 3 incorrect attempts. Your account is locked for 15 minutes.')
                else:
                    remaining_attempts = 3 - user.failed_attempts
                    messages.error(request, f'Invalid email or password. Attempts left: {remaining_attempts}')

                user.save()
        else:
            messages.error(request, 'Invalid email or password.')

    attempts_left = 3 if not user else max(0, 3 - user.failed_attempts)
    return render(request, 'player/login.html', {'attempts_left': attempts_left})


def logout_view(request):
    logout(request)
    return redirect('home')


def forgotpassword(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = players.objects.get(email=email)
        except players.DoesNotExist:
            user = None

        if user:
            otp = random.randint(10000, 99999)
            send_mail(
                'Your OTP Code',
                f'Your OTP code is {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            request.session['otp'] = otp
            request.session['email'] = email
            return redirect('forgototp')

    return render(request, 'player/forgotpassword.html')


def resetpassword(request):
    if request.method == "POST":
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not re.search(r'[A-Za-z]', new_password) or not re.search(r'\d', new_password):
            messages.error(request, 'Password must contain both letters and numbers.')
        elif new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        else:
            try:
                user_email = request.session.get('email')
                user = players.objects.get(email=user_email)
                user.password = make_password(new_password)
                user.save()
                messages.success(request, 'Password reset successful!')
                return redirect('login')
            except players.DoesNotExist:
                messages.error(request, 'User does not exist.')

    return render(request, 'player/resetpassword.html')


def forgototp(request):
    if request.method == "POST":
        otp = request.POST.get('otp')
        session_otp = request.session.get('otp')

        if otp and session_otp and otp == str(session_otp):
            return redirect('resetpassword')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'player/forgototp.html')


def userprofile(request):
    if 'pid' not in request.session:
        return redirect('login')

    try:
        player = players.objects.get(Players_id=request.session['pid'])
    except players.DoesNotExist:
        messages.error(request, 'Player not found.')
        return redirect('login')

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            

            contact_no = request.POST.get('contact_no')
            dob = request.POST.get('dob')
            profile_image = request.FILES.get('profile_image')

            player.first_name = first_name
            player.last_name = last_name

            
            player.contact = contact_no
            player.date_of_birth = dob
            if profile_image:
                player.profile_image = profile_image
            player.save()

            messages.success(request, 'Profile updated successfully')
            return redirect('userprofile')

        elif 'change_password' in request.POST:
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if not check_password(current_password, player.password):
                messages.error(request, 'Current password is incorrect')
            elif new_password != confirm_password:
                messages.error(request, 'New passwords do not match')
            else:
                player.password = make_password(new_password)
                player.save()
                update_session_auth_hash(request, player)
                messages.success(request, 'Password changed successfully')
                return redirect('userprofile')

    return render(request, 'player/userprofile.html', {'player': player})

def game_list(request):
    if 'pid' not in request.session:
        return redirect('login')

    try:
        player = players.objects.get(Players_id=request.session['pid'])
    except players.DoesNotExist:
        return redirect('profile_setup')

    user_games = Library.objects.filter(player=player)
    purchased_games = {game.game.game_id: True for game in user_games}

    games = Game.objects.filter(status='Approved')
    games_by_type = {}
    for game in games:
        game_type = game.game_type
        if game_type not in games_by_type:
            games_by_type[game_type] = []
        games_by_type[game_type].append(game)

    context = {
        'games_by_type': games_by_type,
        'purchased_games': purchased_games
    }

    return render(request, 'player/games.html', context)

def payment_success(request):
    if 'pid' not in request.session:
        return redirect('login')

    if request.method == "POST":
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        logger.info("Received payment details:")
        logger.info(f"Razorpay Payment ID: {razorpay_payment_id}")
        logger.info(f"Razorpay Order ID: {razorpay_order_id}")

        try:
            payment = Payment.objects.get(order_id=razorpay_order_id)
            payment.payment_status = 'Success'
            payment.payment_id = razorpay_payment_id
            payment.save()

            game = payment.game
            player = players.objects.get(Players_id=request.session['pid'])

            Library.objects.create(player=player, game=game)

            logger.info(f"Game '{game.title}' has been successfully added to the player's library.")

            return JsonResponse({'status': 'success', 'message': 'Payment verified and game added to library'})

        except Payment.DoesNotExist:
            logger.error(f"Payment with order ID {razorpay_order_id} does not exist.")
            return JsonResponse({"success": False, "message": "Payment not found."}, status=400)
        except players.DoesNotExist:
            logger.error(f"No player found with pid: {request.session['pid']}")
            return JsonResponse({"success": False, "message": "Player not found."}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return JsonResponse({"success": False, "message": "An error occurred while processing the payment."}, status=500)
        
def create_payment(request, game_id):
    if 'pid' not in request.session:
        return redirect('login')

    game = get_object_or_404(Game, game_id=game_id)  

    if request.method == "POST":
        amount = int(game.price * 100)  
        currency = "INR"

        try:
            order = razorpay_client.order.create({
                'amount': amount,
                'currency': currency,
                'payment_capture': 1  
            })

            payment = Payment.objects.create(
                order_id=order['id'],
                amount=game.price,
                payment_status="Pending",  
                game=game
            )

            return render(request, 'player/payment_page.html', {
                'order_id': order['id'],
                'amount': amount,
                'key_id': settings.RAZORPAY_API_KEY,
                'game': game
            })

        except Exception as e:
            logger.error(f"Error creating Razorpay order: {str(e)}")
            return JsonResponse({"success": False, "message": "An error occurred while creating the payment order."}, status=500)

    return render(request, 'player/create_payment.html', {'game': game})

def library(request):
    if 'pid' not in request.session or not request.session['pid']:
        return redirect('login')

    try:
        player = players.objects.get(Players_id=request.session['pid'])
    except players.DoesNotExist:
        return redirect('login')

    purchased_games = Library.objects.filter(player=player)
    games = Game.objects.filter(id__in=[lib.game.game_id for lib in purchased_games])

    return render(request, 'player/library.html', {'games': games})

def download_game(request, game_id):
    if 'pid' not in request.session or not request.session['pid']:
        return redirect('login')

    player = get_object_or_404(players, Players_id=request.session['pid'])
    game = get_object_or_404(Game, game_id=game_id)

    if not Library.objects.filter(player=player, game=game).exists():
        return HttpResponseForbidden("You don't have access to download this game.")

    file_path = game.game_file.path

    if not os.path.exists(file_path):
        return HttpResponseForbidden("Game file not found.")

    with open(file_path, 'rb') as game_file:
        response = HttpResponse(game_file.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{game.title}.zip"'
        return response
    

from django.http import JsonResponse
from django.shortcuts import redirect
from .models import Payment, Library, players
import logging

logger = logging.getLogger(__name__)

def payment_success(request):
    if 'pid' not in request.session:
        return redirect('login')  

    if request.method == "POST":
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        
        logger.info("Received payment details:")
        logger.info("Razorpay Payment ID: %s", razorpay_payment_id)
        logger.info("Razorpay Order ID: %s", razorpay_order_id)

        
            
        payment = Payment.objects.get(order_id=razorpay_order_id)
        payment.payment_status = 'Success'
        payment.payment_id = razorpay_payment_id
        payment.save()

            
        game = payment.game
        try:
                    player = players.objects.get(Players_id=request.session['pid'])  
        except players.DoesNotExist:
                    
                    logger.error(f"No player found with pid: {request.session['pid']}")
                    return JsonResponse({"success": False, "message": "Player not found."}, status=400)

                
        Library.objects.create(player=player, game=game)

                
        return JsonResponse({'status': 'success', 'message': 'Payment verified'})



@csrf_exempt
def create_payment(request, game_id):
    if 'pid' not in request.session:
        return redirect('login')  
    
    game = get_object_or_404(Game, game_id=game_id)

    if request.method == "POST":
        amount = int(game.price * 100)
        currency = "INR"

        try:
            
            order = razorpay_client.order.create({
                'amount': amount,
                'currency': currency,
                'payment_capture': 1  
            })

            
            payment = Payment.objects.create(
                order_id=order['id'],
                amount=game.price,
                payment_status="Pending",  
                game=game
            )

            return render(request, 'player/payment_page.html', {
                'order_id': order['id'],
                'amount': amount,
                'key_id': settings.RAZORPAY_API_KEY,
                'game': game
            })
        
        except Exception as e:
            logger.error(f"Error creating Razorpay order: {str(e)}")
            return JsonResponse({"success": False, "message": "An error occurred while creating the payment order."}, status=500)

    return render(request, 'player/create_payment.html', {'game': game})



def payment_page(request, game_id):
    if 'pid' not in request.session:
        return redirect('login')  
    game = get_object_or_404(Game, pk=game_id)
    return render(request, 'player/payment_page.html', {'game': game})





def library(request):
    
    if 'pid' not in request.session or not request.session['pid']:
        return redirect('login')  

    try:
        player = players.objects.get(Players_id=request.session['pid'])
    except players.DoesNotExist:
        print(f"No player instance found for pid: {request.session['pid']}")
        return redirect('login')

    purchased_games = Library.objects.filter(player=player)
    games = Game.objects.filter(game_id__in=[lib.game.game_id for lib in purchased_games])


    return render(request, 'player/library.html', {'games': games})


def download_game(request, game_id):
    
    if 'pid' not in request.session or not request.session['pid']:
        return redirect('login')  

    player = get_object_or_404(players, Players_id=request.session['pid'])
    game = get_object_or_404(Game, game_id=game_id)

    
    if not Library.objects.filter(player=player, game=game).exists():
        return HttpResponseForbidden("You don't have access to download this game.")

    file_path = game.game_file.path  

    if not os.path.exists(file_path):
        return HttpResponseForbidden("Game file not found.")

    with open(file_path, 'rb') as game_file:
        response = HttpResponse(game_file.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{game.title}.zip"'
        return response
    


def send_friend_request(request):
    
    player = get_object_or_404(players, Players_id=request.session['pid'])

    
    query = request.GET.get('query', '')

    
    players_list = players.objects.filter(username__icontains=query).exclude(Players_id=player.Players_id)

    
    players_with_add_button = []
    
    for p in players_list:
        
        existing_friendship = Friendship.objects.filter(
            (Q(player1=player, player2=p) | Q(player1=p, player2=player)) 
        ).first()

        if existing_friendship:
            if existing_friendship.status == 'pending':
                players_with_add_button.append({'player': p, 'can_add': False, 'status': 'pending'})
            else:
                players_with_add_button.append({'player': p, 'can_add': False, 'status': 'friends'})
        else:
            players_with_add_button.append({'player': p, 'can_add': True, 'status': 'none'})
    
    return render(request, 'player/player_search.html', {'players': players_with_add_button})

@login_required
def accept_friend_request(request, username):
    try:
        player = get_object_or_404(players, Players_id=request.session['pid'])
        sender = players.objects.get(username=username)

        friendship = Friendship.objects.get(player1=sender, player2=player, status='pending')
        friendship.status = 'accepted'
        friendship.save()

        
        messages.success(request, f'You are now friends with {sender.username}')
        return JsonResponse({'success': f'You are now friends with {sender.username}'})
    except players.DoesNotExist:
        return JsonResponse({'error': 'Player not found'})
    except Friendship.DoesNotExist:
        return JsonResponse({'error': 'Friend request not found or already accepted'})


@login_required
def reject_friend_request(request, username):
    try:
        player = get_object_or_404(players, Players_id=request.session['pid'])
        sender = players.objects.get(username=username)

        friendship = Friendship.objects.get(player1=sender, player2=player, status='pending')
        friendship.status = 'rejected'
        friendship.save()

        
        messages.success(request, f'Friend request from {sender.username} rejected')
        return JsonResponse({'success': f'Friend request from {sender.username} rejected'})
    except players.DoesNotExist:
        return JsonResponse({'error': 'Player not found'})
    except Friendship.DoesNotExist:
        return JsonResponse({'error': 'Friend request not found'})


@login_required
def friends_list(request):
    player = get_object_or_404(players, Players_id=request.session['pid'])

    friendships = Friendship.objects.filter(
        Q(player1=player) | Q(player2=player),
        status='accepted'
    )

    friends = [
        friendship.player1 if friendship.player2 == player else friendship.player2
        for friendship in friendships
    ]

    return render(request, 'player/friends_list.html', {'friends': friends})
