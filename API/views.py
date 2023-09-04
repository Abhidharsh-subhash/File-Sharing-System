from django.shortcuts import render
from .permissions import Is_opsuser,Is_client
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from .serializers import OpsUserLoginSerializer,UploadFileSerializer,FileListSerializer,SignupSerializer,ClientLoginSerializer
from .models import Files
from .models import users
from .send_email import send_mail
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import smart_str,force_str,smart_bytes,DjangoUnicodeDecodeError
from django.db import transaction
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.request import Request
from django.shortcuts import get_object_or_404
from django.http import FileResponse

# Create your views here.

class OpsUserLogin(GenericAPIView):
    serializer_class=OpsUserLoginSerializer
    def post(self,request):
        data=request.data
        serializer=self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data['user']
        tokens=RefreshToken.for_user(user)
        response={
            'message':'Worker login successfull',
            'access':str(tokens.access_token),
            'refresh':str(tokens),
        }
        return Response(data=response,status=status.HTTP_200_OK)
    
class UploadFile(GenericAPIView):
    permission_classes = [Is_opsuser]
    serializer_class=UploadFileSerializer
    def post(self,request):
        data=request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ClientSignup(GenericAPIView):
    serializer_class=SignupSerializer
    def post(self,request):
        serializer=self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')
            try:
                with transaction.atomic():
                    user = users(email=email, username=username)
                    user.set_password(password)
                    user.is_client=True
                    user.save()
                    #encoding the user id
                    uidb64=urlsafe_base64_encode(smart_bytes(user.id))
                    token=PasswordResetTokenGenerator().make_token(user)
                    current_site=get_current_site(request=request).domain
                    relativelink=reverse('PasswordTokenCheck-confirm',kwargs={'uidb64':uidb64,'token':token})
                    redirect_url = request.data.get('redirect_url', '')
                    absurl='http://'+current_site+relativelink
                    email_body='Hello \n Use below link to confirm you E-mail \n'+absurl+"?redirect_url="+redirect_url
                    data={'email_body':email_body,'to_email':user.email,'email_subject':'Confirm Your Email'}
                    send_mail(data)
                    #serializer.save()
                return Response({'message':"User registered successfully",'Action':'Check your mail and get verified'}, status=status.HTTP_201_CREATED)
            except Exception as e:
                print(f"Error during registration: {str(e)}")
                user.delete()
                return Response({'message':'User registration failed'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PasswordTokenCheck(GenericAPIView):
    def get(self,request,uidb64, token):
        redirect_url = request.GET.get('redirect_url')
        try:
            id=smart_str(urlsafe_base64_decode(uidb64))
            user=users.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user,token):
                response={
                    'message':'Toke is not valid request a new one'
                }
                return Response(data=response,status=status.HTTP_401_UNAUTHORIZED)
            user.is_verified = True
            user.save()
            response={
                'success':True,
                'message':'Credentials valid',
                'uidb64':uidb64,
                'token':token
            }
            return Response(data=response,status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError as identifier:
            if not PasswordResetTokenGenerator().check_token(user):
                response={
                    'message':'Token is not valid request a new one'
                }
                return Response(data=response,status=status.HTTP_401_UNAUTHORIZED)

class ClientLogin(GenericAPIView):
    serializer_class=ClientLoginSerializer
    def post(self,request):
        data=request.data
        serializer=self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data['user']
        tokens=RefreshToken.for_user(user)
        response={
            'message':'User login successfull',
            'access':str(tokens.access_token),
            'refresh':str(tokens),
        }
        return Response(data=response,status=status.HTTP_200_OK)

class FileList(GenericAPIView):
    # permission_classes = [Is_client]
    serializer_class=FileListSerializer
    queryset=Files.objects.all()
    def get(self,request):
        data=self.get_queryset()
        if data.exists():
            serializer=self.serializer_class(data,many=True)
            return Response(data=serializer.data,status=status.HTTP_200_OK)
        return Response({'message':"No files found"}, status=status.HTTP_204_NO_CONTENT)
    
class FileDownload(GenericAPIView):
    def get(self,request):
        file_id=request.data.get('file_id')
        uploaded_file = Files.objects.get(pk=file_id)
        response = FileResponse(uploaded_file.file, content_type='application/force-download')
        response['Content-Disposition'] = f'attachment; filename="{uploaded_file.file.name}"'
        return response

