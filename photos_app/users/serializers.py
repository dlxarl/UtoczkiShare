from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password_confirm']

    def validate_username(self, value):
        """
        Валідація унікальності username.
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Користувач з таким ім'ям вже існує.")
        if len(value) < 3:
            raise serializers.ValidationError("Ім'я користувача повинно бути не менше 3 символів.")
        return value

    def validate_email(self, value):
        """
        Валідація email: унікальність та формат.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Користувач з цією поштою вже існує.")
        if not ('@' in value and '.' in value):
            raise serializers.ValidationError("Невірний формат email.")
        return value

    def validate_password(self, value):
        """
        Валідація паролю: мінімальна довжина, складність.
        """
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        
        # Додаткові перевірки
        if value.lower() == self.initial_data.get('username', '').lower():
            raise serializers.ValidationError("Пароль не може дорівнювати ім'ю користувача.")
        
        return value

    def validate(self, attrs):
        """
        Перевірка що паролі збігаються.
        """
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({"password": "Паролі не збігаються."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user