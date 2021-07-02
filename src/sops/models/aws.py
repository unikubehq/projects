import logging

from django.db import models

from .base import SOPSProvider

logger = logging.getLogger("sops.aws")


class AWSKMS(SOPSProvider):

    access_key = models.TextField()
    secret_access_key = models.TextField()

    class Meta:
        verbose_name = "AWS KMS Credential"
        verbose_name_plural = "AWS KMS Credentials"

    @classmethod
    def get_sops_type(cls):
        return "aws"

    def get_environment(self):
        env = super(AWSKMS, self).get_environment()
        env["AWS_SDK_LOAD_CONFIG"] = "1"
        env["AWS_ACCESS_KEY_ID"] = self.access_key
        env["AWS_SECRET_ACCESS_KEY"] = self.secret_access_key
        return env
