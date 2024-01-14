from django.contrib import messages
from django.contrib.auth import login, logout
from django.urls import reverse
from dotenv import load_dotenv
import os
import requests
from django.shortcuts import redirect
from .models import User
from .exceptions import GithubException, SocialLoginException

load_dotenv()

def github_callback(request):
  try:
    if request.user.is_authenticated:
      raise SocialLoginException("User already loggen in")
    code = request.GET.get("code", None)
    if code is None:
      raise GithubException("Can't get code")
    
    client_id = os.getenv('GITHUB_CLIENT_ID')
    client_secret = os.getenv('GITHUB_CLIENT_SECRET')
    
    token_request = requests.post(
      f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}",
      headers={"Accept": "application/json"},
    )
    token_json = token_request.json()
    error = token_json.get("error", None)
    
    if error is not None:
      raise GithubException("Cant' get access token")
    
    access_token = token_json.get("access_token")
    profile_request = requests.get(
      "https://api.github.com/user",
      headers={
        "Authorization": f"token {access_token}",
        "Accept": "application/json",
      }
    )
    profile_json = profile_request.json()
    
    login_id = profile_json.get("id", None)
    if login_id is None:
      raise GithubException("Can't get user ID from profile_request")
    
    username = profile_json.get("login", None)
    if username is None:
      raise GithubException("Can't get username from profile_request")
    
    try:
      user = User.objects.get(login_id=login_id)
    
    except User.DoesNotExist:
      user = User.objects.create(
        login_id=login_id,
        username=username,
      )
      user.save()
      messages.success(request, f"{username} logged in with Github")
    
    login(request, user)
    print('LOGIN')
    return redirect("http://localhost:3000")
  
  except GithubException as error:
    messages.error(request, error)
    return redirect("http://localhost:3000")
  
  except SocialLoginException as error:
    messages.error(request, error)
    return redirect("http://localhost:3000")
  
def logout_view(request):
    print(request.user)
    print(request.session)
    # 사용자가 로그인되어 있지 않은 경우
    if not request.user.is_authenticated:
        messages.info(request, "No user is currently logged in.")
        print('NO')
        return redirect("http://localhost:3000")

    # 로그아웃 실행
    logout(request)
    messages.success(request, "Successfully logged out.")
    print('YES')
    return redirect("http://localhost:3000")