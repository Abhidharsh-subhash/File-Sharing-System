from django.shortcuts import render
from .permissions import Is_opsuser,Is_client
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from .serializers import OpsUserLoginSerializer,UploadFileSerializer,FileListSerializer,SignupSerializer
from .models import Files

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
        pass
    
class FileList(GenericAPIView):
    permission_classes = [Is_client]
    serializer_class=FileListSerializer
    def get(self,request):
        files=Files.objects.all()
        serializer=self.serializer_class(data=files,many=True)
        if not files:
            return Response({'message':"No files found"}, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.data)

