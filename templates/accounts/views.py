from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib import messages
# Create your views here.


def login_view(request):
    if request.method == 'post':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        user = authenticate(request, username=email, password = password)

        if user is not None:
            login(request, user)

            if not remember:
                request.session.set_expiry(0)
            else:
                #Remember it for 30 days
                request.session.set_expiry(60 * 60 * 24 * 30)
            
            return redirect('/')
        else:
            messages.error(request, 'Eposta veya Şifre hatalı.')
        
    return render(request, 'accounts/login.html')
