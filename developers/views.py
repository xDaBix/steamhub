import random
import re
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms import Registration, GameUploadForm, GameImageFormSet
from .models import Developer, Game, GameImage
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import get_object_or_404, redirect



# Home View
def home(request):
    is_logged_in = 'did' in request.session
    return render(request, 'developers/index.html', {'is_logged_in': is_logged_in})


# Sign Up View
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

            # Ensure the correct model name is used here
            email_exists = Developer.objects.filter(email=email).exists()
            username_exists = Developer.objects.filter(username=username).exists()

            if email_exists or username_exists:
                messages.error(request, 'Email or Username already exists.')
                return render(request, 'developers/signup.html', {'form': form})

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
            return redirect('developer_verifyotp')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = Registration()

    return render(request, 'developers/signup.html', {'form': form})


# Login View
def login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = Developer.objects.get(email=email)
        except Developer.DoesNotExist:
            user = None

        if user and check_password(password, user.password):
            request.session['did'] = user.did  
            return redirect('developer_home')
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'developers/login.html')


# Check if User Exists (AJAX request)
def check_user_exists(request):
    if request.method == "GET":
        email = request.GET.get('email', '').strip()
        username = request.GET.get('username', '').strip()

        email_exists = Developer.objects.filter(email=email).exists()
        username_exists = Developer.objects.filter(username=username).exists()

        response = {
            'email_exists': email_exists,
            'username_exists': username_exists,
        }

        return JsonResponse(response)


# OTP Verification View
def verify_otp(request):
    if request.method == "POST":
        otp = request.POST.get('otp')
        registration_data = request.session.get('registration_data')

        if otp and registration_data and int(otp) == registration_data.get('otp'):
            date_of_birth_str = registration_data.get('date_of_birth')
            date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()

            # Check if the email already exists
            if Developer.objects.filter(email=registration_data.get('email')).exists():
                messages.error(request, 'Email already exists. Please log in or use a different email.')
                return redirect('developer_login')

            user = Developer(
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

            request.session['did'] = user.did  

            del request.session['registration_data']

            messages.success(request, 'Registration successful!')
            return redirect('developer_home')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'developers/verify_otp.html')


# Logout View
def logout_view(request):
    logout(request)
    return redirect('developer_home')


# Forgot Password View
def forgotpassword(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = Developer.objects.get(email=email)
        except Developer.DoesNotExist:
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
            return redirect('developer_forgototp')

    return render(request, 'developers/forgotpassword.html')


# Reset Password View
def resetpassword(request):
    if request.method == "POST":
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not re.search(r'[A-Za-z]', new_password) or not re.search(r'\d', new_password):
            messages.error(request, 'Password must contain both letters and numbers.')
        elif new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        else:
            user_email = request.session.get('email')
            try:
                user = Developer.objects.get(email=user_email)
                user.password = make_password(new_password)
                user.save()
                messages.success(request, 'Password reset successful!')
                return redirect('developer_login')
            except Developer.DoesNotExist:
                messages.error(request, 'User does not exist.')

    return render(request, 'developers/resetpassword.html')


# Forgot OTP View
def forgototp(request):
    if request.method == "POST":
        otp = request.POST.get('otp')
        session_otp = request.session.get('otp')

        if otp and session_otp and otp == str(session_otp):
            return redirect('developer_resetpassword')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'developers/forgototp.html')




def userprofile(request):
    if 'did' not in request.session:
        return redirect('developer_login')

    try:
        developer = Developer.objects.get(did=request.session['did'])  
    except Developer.DoesNotExist:
        messages.error(request, 'Developer not found.')
        return redirect('developer_login')

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            contact_no = request.POST.get('contact_no')
            dob = request.POST.get('dob')
            profile_image = request.FILES.get('profile_image')

            developer.first_name = first_name
            developer.last_name = last_name
            developer.contact = contact_no
            developer.date_of_birth = dob
            if profile_image:
                developer.profile_image = profile_image  
            developer.save()

            messages.success(request, 'Profile updated successfully')
            return redirect('developer_profile')

        elif 'change_password' in request.POST:
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if not check_password(current_password, developer.password):
                messages.error(request, 'Current password is incorrect')
            elif new_password != confirm_password:
                messages.error(request, 'New passwords do not match')
            else:
                developer.password = make_password(new_password)
                developer.save()
                update_session_auth_hash(request, developer)
                messages.success(request, 'Password changed successfully')
                return redirect('developer_profile')

    return render(request, 'developers/userprofile.html', {'developer': developer})



def upload_game(request):
    
    if 'did' not in request.session:
        return redirect('developer_login')

    developer = Developer.objects.get(did=request.session['did'])  

    if request.method == 'POST':
        game_form = GameUploadForm(request.POST, request.FILES)
        image_formset = GameImageFormSet(request.POST, request.FILES, queryset=GameImage.objects.none())

        if game_form.is_valid() and image_formset.is_valid():
            
            game = game_form.save(commit=False)  
            game.developer = developer  
            game.save()  

            
            for form in image_formset:
                if form.cleaned_data.get('image'):  
                    GameImage.objects.create(game=game, image=form.cleaned_data['image'])

            return redirect('developer_game_list')  
    else:
        game_form = GameUploadForm()
        image_formset = GameImageFormSet(queryset=GameImage.objects.none())

    return render(request, 'developers/upload_game.html', {
        'game_form': game_form,
        'image_formset': image_formset
    })

def game_list(request):
    if 'did' not in request.session:
        return redirect('developer_login')
    
    developer_id = request.session['did']  
    games = Game.objects.filter(developer_id=developer_id)  
    
    return render(request, 'developers/gamelist.html', {'games': games})

def delete_game(request, game_id):
    game = get_object_or_404(Game, game_id=game_id)
    
    
    game.delete()

    
    return redirect('developer_game_list')