from rest_framework import serializers
from .models import Client, Domain

class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ['id', 'domain', 'is_primary']

class ClientSerializer(serializers.ModelSerializer):
    domains = DomainSerializer(many=True, read_only=True)

    class Meta:
        model = Client
        fields = ['id', 'schema_name', 'name', 'created_on', 'domains']
        read_only_fields = ['created_on']

class TenantCreateSerializer(serializers.ModelSerializer):
    domain = serializers.CharField(write_only=True, help_text='e.g. acmebank.kyc_portal.local')

    class Meta:
        model = Client
        fields = ['schema_name', 'name', 'domain']