# -*- coding: utf-8 -*-
from django.db import models
from util.models import BaseModel
from django.utils.translation import ugettext_lazy as _


class AnalyzeRepository(BaseModel):
    analyzed_at = models.DateTimeField(verbose_name=_("Analyzed at"), auto_now_add=True,
                                       db_index=True)
    database_name = models.CharField(verbose_name=_("Database name"), max_length=60,
                                     unique=False, null=False, blank=False,
                                     db_index=True)
    instance_name = models.CharField(verbose_name=_("Instance name"), max_length=100,
                                     unique=False, null=False, blank=False,
                                     db_index=True)
    engine_name = models.CharField(verbose_name=_("Engine name"), max_length=20,
                                   unique=False, null=False, blank=False,
                                   db_index=True)
    environment_name = models.CharField(verbose_name=_("Environment name"), max_length=30,
                                        unique=False, null=False, blank=False,
                                        db_index=True)
    cpu_alarm = models.BooleanField(verbose_name=_("CPU alarm"), default=False)
    memory_alarm = models.BooleanField(verbose_name=_("Memory alarm"), default=False)
    email_sent = models.BooleanField(verbose_name=_("Memory alarm"), default=False,
                                     db_index=True)

    class Meta:
        unique_together = (
            ('analyzed_at', 'instance_name',)
        )
        permissions = (
            ("view_analyzerepository", "Can view analyze repository"),
        )



class ExecutionPlan(BaseModel):
    plan_name = models.CharField(verbose_name=_("Execution plan name"), max_length=60,
                                     unique=True, null=False, blank=False,
                                     db_index=True)
    metrics = models.CharField(verbose_name=_("Metrics used by plan"), max_length=200,
                               unique=True, null=False, blank=False, db_index=True,
                               help_text='Comma separated list of metrics. Ex.: cpu.cpu_used,cpu.cpu_free,...')
    threshold = models.IntegerField(verbose_name=_("Threshold"), unique=False,
                                    null=False, default=50)
    proccess_function = models.CharField(verbose_name=_("Proccess function used by service"),
                                         max_length=150, unique=False, null=False, blank=False,)
    adapter = models.CharField(verbose_name=_("Adapter used by service"),
                               max_length=150, unique=False, null=False, blank=False,)

    class Meta:
        permissions = (
            ("view_executionplan", "Can view Execution Plan"),
        )
