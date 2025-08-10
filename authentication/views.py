from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from Login import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import  urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token
from django.core.mail import EmailMessage, send_mail

# Create your views here.
def home(request):
    return render (request, "authentication/index.html")

def signup(request):
    if request.method == "POST":
        # username = request.POST.get("username")
        username = request.POST["username"]
        firstname = request.POST["firstname"]
        lastname = request.POST["lastname"]
        email= request.POST["email"]
        password= request.POST["password"]
        confirmpassword= request.POST["confirmpassword"]


        if User.objects.filter(username=username):
            messages.error(request,"Username already exist! Please try another username")
            return redirect("home")
        
        if User.objects.filter(email=email):
            messages.error(request,"Account already exist")
            return redirect("home")
        
        if len(username) > 10:
            messages.error(request,"username must be under 10 characters")

        if password != confirmpassword:
            messages.error(request,"Password do not match")

        if not username .isalnum():
            messages.error(request,"Username must be alpha numeric")
            return redirect("home")

        # create a user object
        myuser= User.objects.create_user(username = username, email= email, password= password)
        myuser.first_name =  firstname
        myuser.last_name =  lastname
        myuser.is_active = False

        myuser.save()
        messages.success(request,"Your Account has been successfully created.We have sent you a confirmation email, please check")


        # Welcome Email

        subject = "Welcome to GFG - DJANGO login!"
        message = "Hello" + myuser.first_name + "!! \n" + "Welcome to GFG \n Thankyou for visiting our website \n We have also sent you a confrimation email, Please confirm your email addressn to order your email address Thankyou!"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently = False)
        
        #Email address confirmation email
        
        current_site = get_current_site(request)
        email_subject = "confrim your email @ GFG -Django Login!!"
        message2 = render_to_string("email_confirmation.html",{
            "name": myuser.first_name,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(myuser.pk)),
            "token": generate_token.make_token(myuser)
        })
                                    
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = False
        email.send()
                                
        
        
        return redirect('signin')
    return render(request,"authentication/signup.html")


def signin(request):
    if request.method=="POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user =  authenticate(username= username, password= password)
        
        if user is not None:
            login(request,user)
            firstname = user.first_name
            return render(request, "authentication/index.html", {'firstname':firstname}) 
        else:
            messages.error(request, "Invalid credentials")
            return redirect('home')
            
    return render(request, "authentication/signin.html")

def signout(request):
    logout(request)
    messages.success(request,"successfully logged out")
    return redirect("home")


def activate(request, uidb64, token):
    try:
        uid = force_str (urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None
        
    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('home')
    else:
        return render(request, "activation_failed.html")
    