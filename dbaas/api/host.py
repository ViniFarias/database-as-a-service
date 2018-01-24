# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from rest_framework import viewsets, serializers, permissions
from rest_framework import filters
from django.core.exceptions import ObjectDoesNotExist
from util import get_credentials_for
from dbaas_credentials.models import CredentialType

from physical.models import Host


class HostSerializer(serializers.ModelSerializer):
    team_name = serializers.SerializerMethodField('get_team_name')
    env_name = serializers.SerializerMethodField('get_env_name')
    region_name = serializers.SerializerMethodField('get_region_name')
    offering = serializers.SerializerMethodField('get_offering')
    disks = serializers.SerializerMethodField('get_disks')
    project_id = serializers.SerializerMethodField('get_project_id')
    database = serializers.SerializerMethodField('get_database_metadata')
    identifier = serializers.SerializerMethodField('get_vm_id')

    class Meta:
        model = Host
        fields = (
            'id',
            'os_description',
            'updated_at',
            'created_at',
            'team_name',
            'env_name',
            'region_name',
            'hostname',
            'identifier',
            'offering',
            'disks',
            'project_id',
            'database'
        )

    def get_vm_id(self, host):
        host_attr = host.cs_host_attributes.first()

        return host_attr and host_attr.vm_id

    def get_database(self, host):
        first_instance = host.instances.first()
        database = first_instance and first_instance.databaseinfra.databases.first()

        return database

    def get_database_metadata(self, host):
        database = self.get_database(host)

        if database is None:
            return {}
        return {
            'project_name': database.project and database.project.name,
            'engine': str(database.engine),
            'name': database.name,
            'id': database.id,
            'infra': {
                'id': database.infra.id,
                'name': database.infra.name
            }
        }

    def get_team_name(self, host):
        database = self.get_database(host)

        return database and database.team.name

    def get_env(self, host):
        database = self.get_database(host)

        return database and database.environment

    def get_env_name(self, host):
        env = self.get_env(host)

        return env and env.name

    def get_project_id(self, host):
        env = self.get_env(host)

        credential = get_credentials_for(
            env, CredentialType.CLOUDSTACK)

        return credential and credential.project

    def get_region_name(self, host):
        env = self.get_env(host)
        try:
            return env and env.cs_environment_region.first().name
        except ObjectDoesNotExist:
            return

    def get_disks(self, host):
        return map(
            lambda d: {
                'active': d.is_active,
                'total': d.nfsaas_size_kb,
                'used': d.nfsaas_used_size_kb,
                'export_id': d.nfsaas_export_id
            }, host.nfsaas_host_attributes.all())

    def get_offering(self, host):
        offering = host.offering
        if offering:
            return {
                'type': '{}c{}'.format(offering.cpus, offering.memory_size_mb),
                'cpus': offering.cpus,
                'memory': offering.memory_size_mb
            }
        return {}


class HostAPI(viewsets.ReadOnlyModelViewSet):

    """
    Host API
    """

    model = Host
    serializer_class = HostSerializer
    queryset = Host.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.OrderingFilter,)
    filter_fields = (
        'id',
        'os_description',
        'updated_at',
        'created_at',
        'hostname'
    )
    ordering_fields = ('created_at', 'updated_at', 'id')
    ordering = ('-created_at',)
    datetime_fields = ('created_at', 'updated_at')

    def get_queryset(self, *args, **kw):
        def has_database(host):
            first_instance = host.instances.first()
            if not first_instance:
                return False
            return first_instance and first_instance.databaseinfra.databases.exists()

        hosts = Host.objects.all()
        filtered_hosts = filter(lambda h: has_database(h), hosts)
        host_ids = map(lambda h: h.id, filtered_hosts)

        return hosts.filter(id__in=host_ids)
