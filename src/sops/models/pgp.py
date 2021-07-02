import logging

from django.db import models

from .base import SOPSProvider

logger = logging.getLogger("sops.pgp")


class PGPKey(SOPSProvider):
    private_key = models.TextField()

    class Meta:
        verbose_name = "PGP Private Key"
        verbose_name_plural = "PGP Private Keys"

    @classmethod
    def get_sops_type(cls):
        return "pgp"

    def get_environment(self):
        env = super(PGPKey, self).get_environment()
        env["PGP_PRIVATE_KEY"] = self.private_key
        return env
