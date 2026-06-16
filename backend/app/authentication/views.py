from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError

from .models import CustomUser
from .serializers import (
    LoginSerializer,
    UserSerializer,
    RegisterSerializer,
    ChangePasswordSerializer,
)
from .permissions import IsAdministrador


def get_tokens_for_user(user):
    """Genera par de tokens JWT (refresh + access) para el usuario."""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access':  str(refresh.access_token),
    }


class LoginView(APIView):
    """
    POST /api/auth/login/
    Body: { username, password }
    Respuesta: { access, refresh, user }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user   = serializer.validated_data['user']
        tokens = get_tokens_for_user(user)

        return Response({
            **tokens,
            'user': UserSerializer(user).data,
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Body: { refresh }
    Invalida el refresh token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': 'Se requiere el refresh token.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'mensaje': 'Sesión cerrada correctamente.'}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({'error': 'Token inválido o expirado.'}, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    """
    GET /api/auth/me/
    Retorna los datos del usuario autenticado.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        """Actualiza nombre, apellido, teléfono del usuario."""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    """
    POST /api/auth/register/
    Solo administradores pueden crear usuarios nuevos.
    """
    permission_classes = [IsAuthenticated, IsAdministrador]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(APIView):
    """
    GET  /api/auth/users/   → Lista todos los usuarios (solo Admin)
    """
    permission_classes = [IsAuthenticated, IsAdministrador]

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class UserDetailView(APIView):
    """
    GET    /api/auth/users/<id>/   → Detalle de un usuario
    PATCH  /api/auth/users/<id>/   → Editar rol / datos
    DELETE /api/auth/users/<id>/   → Desactivar usuario
    """
    permission_classes = [IsAuthenticated, IsAdministrador]

    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return None

    def get(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(UserSerializer(user).data)

    def patch(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        user.activo = False
        user.is_active = False
        user.save()
        return Response({'mensaje': 'Usuario desactivado.'}, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    """
    POST /api/auth/change-password/
    Cambia la contraseña del usuario autenticado.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if not user.check_password(serializer.validated_data['password_actual']):
            return Response(
                {'error': 'La contraseña actual es incorrecta.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data['password_nuevo'])
        user.save()
        return Response({'mensaje': 'Contraseña actualizada correctamente.'})