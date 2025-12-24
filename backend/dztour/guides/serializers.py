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
    user = UserSerializer(read_only=True)
    languages_spoken = LanguageSerializer(many=True, read_only=True)
    wilaya_covered = WilayaSerializer(many=True, read_only=True)
    commune_covered = CommuneSerializer(many=True, read_only=True)
    certifications = CertificationSerializer(many=True, read_only=True)
    
    class Meta:
        model = GuideProfile
        fields = '__all__'
        read_only_fields = ['user', 'is_verified', 'verified_at', 'created_at', 'updated_at']


class GuideProfileCreateUpdateSerializer(serializers.ModelSerializer):
    languages_spoken = serializers.PrimaryKeyRelatedField(
        queryset=Language.objects.all(), many=True, required=False
    )
    wilaya_covered = serializers.PrimaryKeyRelatedField(
        queryset=Wilaya.objects.all(), many=True, required=False
    )
    commune_covered = serializers.PrimaryKeyRelatedField(
        queryset=Commune.objects.all(), many=True, required=False
    )
    
    class Meta:
        model = GuideProfile
        fields = [
            'id_document', 'bio', 'languages_spoken',
            'price_for_half_day', 'price_for_day', 'price_for_sup_hours',
            'wilaya_covered', 'commune_covered',
            'phone_number', 'whatsapp_number', 'instagram_account'
        ]

    def create(self, validated_data):
        languages = validated_data.pop('languages_spoken', [])
        wilayas = validated_data.pop('wilaya_covered', [])
        communes = validated_data.pop('commune_covered', [])
        
        profile = GuideProfile.objects.create(**validated_data)
        profile.languages_spoken.set(languages)
        profile.wilaya_covered.set(wilayas)
        profile.commune_covered.set(communes)
        return profile

    def update(self, instance, validated_data):
        languages = validated_data.pop('languages_spoken', None)
        wilayas = validated_data.pop('wilaya_covered', None)
        communes = validated_data.pop('commune_covered', None)


        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if languages is not None:
            instance.languages_spoken.set(languages)
        if wilayas is not None:
            instance.wilaya_covered.set(wilayas)
        if communes is not None:
            instance.commune_covered.set(communes)
        
        return instance
    

