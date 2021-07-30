from gql.schema.mutation import SOPSTypeEnum
from gql.test_utils import SopsTestsMixin
from gql.tests import SnapshotGraphQLTestCase
from sops.models.aws import AWSKMS
from sops.models.pgp import PGPKey
from sops.tests.factories.aws_factory import AWSKMSFactory
from sops.tests.factories.pgp_factory import PGPKeyFactory


class AWSSopsTests(SopsTestsMixin, SnapshotGraphQLTestCase):
    SOPS_TYPE = SOPSTypeEnum.aws.value
    MODEL = AWSKMS

    @classmethod
    def get_factory(cls):
        return AWSKMSFactory


class PGPSopsTests(SopsTestsMixin, SnapshotGraphQLTestCase):
    SOPS_TYPE = SOPSTypeEnum.pgp.value
    MODEL = PGPKey

    @classmethod
    def get_factory(cls):
        return PGPKeyFactory
