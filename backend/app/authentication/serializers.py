from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            username=data.get('username'),
            password=data.get('password'),
        )
        if not user:
            raise serializers.ValidationError('Credenciales inválidas.')
        if not user.is_active:
            raise serializers.ValidationError('Usuario inactivo.')
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    """Serializa datos del usuario autenticado (sin password)."""

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email',
            'first_name', 'last_name',
            'rol', 'telefono', 'activo',
            'creado_en',
        ]
        read_only_fields = ['id', 'creado_en']


class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, label='Confirmar contraseña')

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'rol', 'telefono', 'password', 'password2',
        ]

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': 'Las contraseñas no coinciden.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    password_actual = serializers.CharField(write_only=True)
    password_nuevo  = serializers.CharField(write_only=True, min_length=8)
    password_nuevo2 = serializers.CharField(write_only=True, label='Confirmar nueva contraseña')

    def validate(self, data):
        if data['password_nuevo'] != data['password_nuevo2']:
            raise serializers.ValidationError({'password_nuevo': 'Las contraseñas no coinciden.'})
        return data