from rest_framework import serializers
from .models import Photo, PhotoShare
from django.contrib.auth.models import User

class PhotoSerializer(serializers.ModelSerializer):
    original_name = serializers.CharField(required=False, allow_blank=True)
    file = serializers.FileField(required=True)
    isOwned = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = ['id', 'original_name', 'file', 'created_at', 'isOwned']

    def get_isOwned(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.owner == request.user
        return False

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.file and instance.file.name:
            data['file'] = instance.file.name
        return data

class PhotoShareSerializer(serializers.ModelSerializer):
    shared_to = serializers.EmailField(write_only=True)

    class Meta:
        model = PhotoShare
        fields = ['id', 'photo', 'created_at', 'shared_to']
        read_only_fields = ['id', 'created_at'] # 'photo' must be provided

    def validate_shared_to(self, value):
        """
        Validate that the email belongs to an existing user and not the requesting user.
        """
        request_user = self.context.get('request').user
        
        if value.lower() == request_user.email.lower():
            raise serializers.ValidationError("You can't share photo with youself.")
        
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User with email {value} does not exist.")
        
        return value