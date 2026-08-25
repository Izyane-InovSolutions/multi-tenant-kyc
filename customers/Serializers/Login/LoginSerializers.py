from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})


class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField(
        required=False,
        help_text="Required for mobile clients only; web clients use the httponly refresh cookie."
    )