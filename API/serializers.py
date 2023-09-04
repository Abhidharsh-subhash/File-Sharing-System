from rest_framework import serializers
from django.core.validators import EmailValidator
from django.core.validators import RegexValidator
from .models import users,Files
from django.contrib.auth import authenticate

class UsernameValidator(RegexValidator):
    regex = r'^[a-zA-Z]+$'
    message = "Enter a valid username with only characters."

class OpsUserLoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(validators=[EmailValidator()])
    password=serializers.CharField(style={'input-type':'password'})
    class Meta:
        model = users
        fields = ['email','password']
    def validate(self, attrs):
        email=attrs.get('email')
        password=attrs.get('password')
        if email and password:
            user=authenticate(email=email,password=password)
            if user:
                if not user.is_superuser:
                    raise serializers.ValidationError('You are not authorized to perform this action')
                else:
                    attrs['user']=user
            else:
                raise serializers.ValidationError('Invalid Username or Password')
        else:
            raise serializers.ValidationError('Username and Password are required')
        return attrs
    
class UploadFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = ['file', 'Uploaded_at']
    def validate_file(self, value):
        file_extension = value.name.split('.')[-1].lower()
        allowed_extensions = ['pptx', 'docx', 'xlsx']
        if file_extension not in allowed_extensions:
            raise serializers.ValidationError("Only pptx, docx, and xlsx files are allowed.")
        return value
    
class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = users
        fields = ['email','username','password']
    
class FileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Files
        fields = ['file', 'Uploaded_at']
