from rest_framework import serializers
from ...models import Client, Domain


class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ['id', 'domain', 'is_primary']


class ClientSerializer(serializers.ModelSerializer):
    domains = DomainSerializer(many=True, read_only=True)

    logo = serializers.ImageField(
        required=False,
        allow_null=True
    )

    primary_color = serializers.CharField(
        required=False,
        allow_blank=True,
        default='#1A73E8',
        help_text="Hex color, e.g. #1A73E8"
    )

    secondary_color = serializers.CharField(
        required=False,
        allow_blank=True,
        default='#F5F5F5',
        help_text="Hex color, e.g. #F5F5F5"
    )

    class Meta:
        model = Client
        fields = [
            'id',
            'tenant_id',
            'schema_name',
            'name',
            'customer_name',

            'tpin',
            'company_registration_number',

            'address',
            'billing_address',
            'shipping_address',

            'phone_no',
            'contact_person_email',
            'contact_person_phone',
            'contact_person_position',

            'logo',
            'primary_color',
            'secondary_color',

            'created_on',
            'domains',
            'status',
        ]

        read_only_fields = [
            'tenant_id',
            'schema_name',
            'created_on',
        ]


class TenantCreateSerializer(serializers.ModelSerializer):
    domain = serializers.CharField(
        write_only=True,
        help_text="e.g. acmebank.kyc_portal.local"
    )

    logo = serializers.ImageField(
        required=False,
        allow_null=True
    )

    primary_color = serializers.CharField(
        required=False,
        allow_blank=True,
        default='#1A73E8',
        help_text="Hex color, e.g. #1A73E8"
    )

    secondary_color = serializers.CharField(
        required=False,
        allow_blank=True,
        default='#F5F5F5',
        help_text="Hex color, e.g. #F5F5F5"
    )

    class Meta:
        model = Client

        fields = [
            'name',
            'customer_name',

            'tpin',
            'company_registration_number',

            'address',
            'billing_address',
            'shipping_address',

            'phone_no',
            'contact_person_email',
            'contact_person_phone',
            'contact_person_position',

            'logo',
            'primary_color',
            'secondary_color',

            'domain',
        ]

    def validate_domain(self, value):
        value = value.strip().lower()

        if Domain.objects.filter(domain__iexact=value).exists():
            raise serializers.ValidationError(
                f"The domain '{value}' is already registered to another tenant."
            )

        return value

    def validate_tpin(self, value):
        value = value.strip()

        if value:
            if not value.isdigit() or len(value) != 10:
                raise serializers.ValidationError(
                    "TPIN must be exactly 10 digits, e.g. 1000000000."
                )

            if Client.objects.filter(tpin=value).exists():
                raise serializers.ValidationError(
                    f"A tenant with TPIN '{value}' already exists."
                )

        return value

    def validate_company_registration_number(self, value):
        value = value.strip()

        if value:
            if Client.objects.filter(
                company_registration_number__iexact=value
            ).exists():
                raise serializers.ValidationError(
                    f"A tenant with registration number '{value}' already exists."
                )

        return value

    def validate_name(self, value):
        return value.strip()