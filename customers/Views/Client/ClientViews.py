from ...models import Client, Domain, generate_unique_schema_name, generate_unique_tenant_id
from ...Serializers.Client.ClientSerializers import ClientSerializer, TenantCreateSerializer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from django.http import Http404




class TenantListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="List all tenants",
        responses=ClientSerializer(many=True),
        tags=["Tenant"]
    )
    def get(self, request):
        try:
            tenants = Client.objects.exclude(schema_name='public')
            serializer = ClientSerializer(tenants, many=True)
            return Response(
                {
                    "status": "success",
                    "message": "Tenants fetched successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"status": "fail", "message": "Something went wrong", "data": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TenantSignUpView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @extend_schema(
        summary="Provision a new tenant",
        description="Creates a tenant schema, runs its migrations, and registers its domain. "
                     "schema_name and tenant_id are generated automatically.",
        request=TenantCreateSerializer,
        responses={201: ClientSerializer},
        tags=["Sign Up"],
    )
    def post(self, request):
        try:
            serializer = TenantCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            domain_name = data.pop('domain')

            schema_name = generate_unique_schema_name(data['name'])
            tenant_id = generate_unique_tenant_id()

            with transaction.atomic():
                client = Client.objects.create(
                    schema_name=schema_name,
                    tenant_id=tenant_id,
                    **data,
                )
                Domain.objects.create(domain=domain_name, tenant=client, is_primary=True)

            return Response(
                {
                    "status": "success",
                    "message": "Tenant provisioned successfully",
                    "data": ClientSerializer(client).data,
                },
                status=status.HTTP_201_CREATED,
            )
        except ValidationError as e:
            return Response(
                {"status": "fail", "message": e.detail, "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"status": "fail", "message": "Something went wrong", "data": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TenantDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        return get_object_or_404(Client, pk=pk)

    @extend_schema(summary="Retrieve a tenant", responses=ClientSerializer, tags=["Tenants"])
    def get(self, request, pk):
        try:
            client = self.get_object(pk)
            serializer = ClientSerializer(client)
            return Response(
                {
                    "status": "success",
                    "message": "Tenant fetched successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Http404:
            return Response(
                {"status": "fail", "message": "Tenant not found", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"status": "fail", "message": "Something went wrong", "data": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(summary="Update a tenant", request=ClientSerializer, responses=ClientSerializer, tags=["Tenants"])
    def patch(self, request, pk):
        try:
            client = self.get_object(pk)
            serializer = ClientSerializer(client, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Tenant updated successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Http404:
            return Response(
                {"status": "fail", "message": "Tenant not found", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ValidationError as e:
            return Response(
                {"status": "fail", "message": "Validation error", "data": e.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"status": "fail", "message": "Something went wrong", "data": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(summary="Deactivate a tenant (soft delete)", tags=["Tenants"])
    def delete(self, request, pk):
        try:
            client = self.get_object(pk)
            if not client.status:
                return Response(
                    {"status": "fail", "message": "Tenant is already deactivated", "data": None},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            client.status = False
            client.save(update_fields=['status'])
            return Response(
                {"status": "success", "message": "Tenant deactivated successfully", "data": None},
                status=status.HTTP_200_OK,
            )
        except Http404:
            return Response(
                {"status": "fail", "message": "Tenant not found", "data": None},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"status": "fail", "message": "Something went wrong", "data": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )