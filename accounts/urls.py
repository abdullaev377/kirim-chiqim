from django.urls import path
from .views import SignUpView, CodeVerify, GetNewCodeView, ChangeInfoView,\
    TokenRefresh, ChangePhotoView, LoginView, LogoutView, ProfileView

urlpatterns = [
    path('signup', SignUpView.as_view()),
    path('code-verify', CodeVerify.as_view()),
    path('new-code', GetNewCodeView.as_view()),
    path('change-info', ChangeInfoView.as_view()),
    path('change-photo', ChangePhotoView.as_view()),
    path('token-refresh', TokenRefresh.as_view()),
    path('login', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('profile', ProfileView.as_view()),
]
