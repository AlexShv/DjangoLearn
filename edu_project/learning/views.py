from django.contrib.auth import login, logout, authenticate, get_user_model
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from .forms import RegistrationForm, LoginForm
from .models import *
from django.contrib import messages
from .generate_tokens import activation_token
from django.utils.safestring import mark_safe
from functools import wraps


def show_categories(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        categories = Category.objects.all()
        return func(request, *args, **kwargs, categories=categories)
    return wrapper


def activate_email(request, user, to_email):
    mail_subject = 'Activate your user account.'
    message = render_to_string('registration/template_activate_account.html', {
        'user': user,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, mark_safe(f'Dear <b>{user}</b>, please go to your email <b>{to_email}</b> and click on \
            received activation link to confirm and complete the registration. <b>Note:</b> Check your spam folder.'))
    else:
        messages.error(request, f'Problem sending confirmation email to {to_email}, check if you typed it correctly.')


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid!')

    return redirect('main_page')


def register_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activate_email(request, user, form.cleaned_data.get('email'))
            return redirect('main_page')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = RegistrationForm()

    return render(
        request,
        'registration/register.html',
        {'title': 'Registration', 'form': form}
    )


def login_user(request):
    if request.user.is_authenticated:
        return redirect('main_page')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Successfully logged in!')
                return redirect('main_page')
    else:
        form = LoginForm()

    return render(
        request,
        'registration/login.html',
        {'title': 'Sign in', 'form': form}
    )


def logout_user(request):
    logout(request)
    return render(
        request,
        'registration/logout.html',
        {'title': 'Sign out'}
    )


@show_categories
def main(request, categories):
    new_courses = Course.objects.order_by('-created_at')[:8]
    return render(
        request,
        'learning/main.html',
        {
            'title': 'Main Page',
            'categories': categories,
            'new_courses': new_courses,
        }
    )


@show_categories
def profile(request, username, categories):
    user = User.objects.get(username=username)
    return render(
        request,
        'learning/profile.html',
        {
            'title': f'{user}\'s Profile',
            'categories': categories
        }
    )


@show_categories
def course_detail(request, course_id, categories):
    course = Course.objects.get(pk=course_id)
    return render(
        request,
        'learning/profile.html',
        {
            'title': course.title,
            'course': course,
            'categories': categories
        }
    )


@show_categories
def courses_catalog(request, categories, category):
    selected_category = Category.objects.get(name=category)
    courses_in_category = Course.objects.filter(category=selected_category)
    return render(
        request,
        'learning/courses_catalog.html',
        {
            'title': 'Courses Catalog',
            'categories': categories,
            'courses_in_category': courses_in_category
        }
    )
