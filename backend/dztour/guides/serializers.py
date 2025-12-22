from rest_framework import serializers
from .models import *
from  users.serializers import * 



class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language 
        fields = '__all__'

class WilayaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wilaya
        fields = '__all__'


class CommuneSerializer(serializers.ModelSerializer):
    wilaya = WilayaSerializer(read_only=True)
    
    class Meta:
        model = Commune
        fields = '__all__'


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certifications
        fields = ['id', 'name', 'file']
        read_only_fields = ['id']   


class GuideProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = GuideProfile
        fields = '__all__'