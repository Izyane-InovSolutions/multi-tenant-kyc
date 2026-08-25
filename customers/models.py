import re
import random
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin


def generate_unique_schema_name(company_name):
    base = re.sub(r'[^a-z0-9]+', '_', company_name.lower()).strip('_')
    if not base or not base[0].isalpha():
        base = f"t_{base}"
    base = base[:40]

    schema_name = base
    counter = 1
    while Client.objects.filter(schema_name=schema_name).exists():
        schema_name = f"{base}_{counter}"
        counter += 1
    return schema_name


def generate_unique_tenant_id():
    """6-digit random number, e.g. 481203. Retries on collision."""
    while True:
        candidate = random.randint(100000, 999999)
        if not Client.objects.filter(tenant_id=candidate).exists():
            return candidate


def tenant_logo_path(instance, filename):
    return f"tenant_logos/{instance.schema_name or 'pending'}/{filename}"


class Client(TenantMixin):
    tenant_id = models.PositiveIntegerField(unique=True, editable=False,  blank=True, null=True)
    name = models.CharField(max_length=150, help_text="Company / organisation name")
    customer_name = models.CharField(max_length=150, blank=True, help_text="Primary contact person")

    tpin = models.CharField(max_length=20, blank=True, verbose_name="TPIN")
    company_registration_number = models.CharField(max_length=50, blank=True)

    address = models.TextField(blank=True, help_text="Registered / physical address")
    billing_address = models.TextField(blank=True)
    shipping_address = models.TextField(blank=True)

    logo = models.ImageField(upload_to='client_logos/', blank=True, null=True)
    primary_color = models.CharField(
        max_length=7, blank=True, default='#000000',
        help_text="Hex color, e.g. #1A73E8"
    )
    secondary_color = models.CharField(
        max_length=7, blank=True, default='#FFFFFF',
        help_text="Hex color, e.g. #F5F5F5"
    )

    created_on = models.DateField(auto_now_add=True)
    status = models.BooleanField(default=True)

    auto_create_schema = True

    def __str__(self):
        return f"{self.name} ({self.tenant_id})"


class Domain(DomainMixin):
    pass