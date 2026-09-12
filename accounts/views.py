from django.shortcuts import render
from django.conf import settings
from .models import CODE_VERIFY, DONE, NEW, CustomUser, VIA_EMAIL,VIA_PHONE
from .serializer import ProfileSerializer, SignUpSerializer, ChangeInfoSerializer, ChangePhotoSerializer, LoginSerializer, VerifyCodeSerializer
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from datetime import datetime
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError



class SignUpView(CreateAPIView):
    permission_classes = [AllowAny]
    queryset = CustomUser.objects.all()
    serializer_class = SignUpSerializer
    
    
class CodeVerify(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = VerifyCodeSerializer(instance=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            'id': user.id,
            'auth_status': user.auth_status,
            'msg': 'code verified',
            'token': user.token()
        })
    


class GetNewCodeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        self.check_active_code(user)
        if user.auth_type == VIA_EMAIL:
            code = user.generate_code(VIA_EMAIL)
            #send_mail(user.email, code)
            print(f'---------------EMAIL CODE: {code} ------------------------')
        elif user.auth_type == VIA_PHONE:
            code = user.generate_code(VIA_PHONE)
            #send_phone_number(user.phone_number, code)
            print(f'---------------SMS CODE: {code} ------------------------')
        else:
            raise ValidationError(
                { 'msg': 'Siz xato email yoki telefon raqam kiritdingiz',
                'status': status.HTTP_400_BAD_REQUEST}
                )
        user.save()
        
        response_data = {
            'msg': "Kod yuborildi",
            'status': status.HTTP_201_CREATED
        }
        if settings.DEBUG:
            response_data['verification_code'] = code
        return Response(response_data)
        
        
        
    @staticmethod
    def check_active_code(user):
        code = user.codes.filter(is_used=False, expire_time__gte=timezone.now()).first()
        if code:
            raise ValidationError(
                { 'msg': 'Siz yangi code ololmaysiz. Sababi sizda hali aktive code bor',
                'status': status.HTTP_400_BAD_REQUEST}
                )
            
        if user.auth_status != NEW:
            raise ValidationError(
                { 'msg': 'Sizga yangi kod berilmaydi',
                'status': status.HTTP_400_BAD_REQUEST}
                )
        return True
    
    
class ChangeInfoView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangeInfoSerializer
    queryset = CustomUser.objects.all()
    
    def get_object(self):
        return self.request.user
    
    
class TokenRefresh(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class ProfileView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user
        
        
class ChangePhotoView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePhotoSerializer
    queryset = CustomUser.objects.all()
    
    def get_object(self):
        return self.request.user
    

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        tokens = user.token()

        return Response({
            "msg": "Muvaffaqiyatli login qilindi",
            "access": tokens['access'],
            "refresh": tokens['refresh']
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({
                'msg': 'Muvaffaqiyatli logout qilindi.'
                })
            
        except TokenError:
            return Response({'detail': 'Invalid or expired refresh token.'}, status=status.HTTP_400_BAD_REQUEST)
    

