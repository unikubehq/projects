from django.contrib import admin
from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicChildModelFilter, PolymorphicParentModelAdmin

from sops.models.aws import AWSKMS
from sops.models.base import SOPSProvider
from sops.models.pgp import PGPKey


class SOPSProviderAdmin(PolymorphicParentModelAdmin):
    """ The parent model admin """

    base_model = SOPSProvider  # Optional, explicitly set here.
    child_models = (AWSKMS, PGPKey)
    list_filter = (PolymorphicChildModelFilter,)  # This is optional.


class AWSKMSAdmin(PolymorphicChildModelAdmin):
    base_model = AWSKMS


class PGPKeyAdmin(PolymorphicChildModelAdmin):
    base_model = PGPKey


admin.site.register(SOPSProvider, SOPSProviderAdmin)
admin.site.register(AWSKMS, AWSKMSAdmin)
admin.site.register(PGPKey, PGPKeyAdmin)
