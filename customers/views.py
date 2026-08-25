# customers/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Client, Domain
from .serializers import ClientSerializer, TenantCreateSerializer


class TenantListCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="List all tenants",
        responses=ClientSerializer(many=True),
    )
    def get(self, request):
        tenants = Client.objects.exclude(schema_name='public')
        serializer = ClientSerializer(tenants, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Provision a new tenant",
        description="Creates a tenant schema, runs its migrations, and registers its domain.",
        request=TenantCreateSerializer,
        responses={201: ClientSerializer},
    )
    def post(self, request):
        serializer = TenantCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        domain_name = data.pop('domain')

        with transaction.atomic():
            client = Client.objects.create(**data)  # triggers schema creation + migrations
            Domain.objects.create(domain=domain_name, tenant=client, is_primary=True)

        return Response(ClientSerializer(client).data, status=status.HTTP_201_CREATED)


class TenantDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Client, pk=pk)

    @extend_schema(summary="Retrieve a tenant", responses=ClientSerializer)
    def get(self, request, pk):
        client = self.get_object(pk)
        return Response(ClientSerializer(client).data)

    @extend_schema(summary="Update a tenant", request=ClientSerializer, responses=ClientSerializer)
    def patch(self, request, pk):
        client = self.get_object(pk)
        serializer = ClientSerializer(client, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(summary="Delete a tenant (drops schema)")
    def delete(self, request, pk):
        client = self.get_object(pk)
        client.delete(force_drop=True)
        return Response(status=status.HTTP_204_NO_CONTENT)