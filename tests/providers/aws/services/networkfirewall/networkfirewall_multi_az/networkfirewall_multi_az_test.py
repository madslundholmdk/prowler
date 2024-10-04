from unittest import mock

from prowler.providers.aws.services.networkfirewall.networkfirewall_service import (
    Firewall,
    IPAddressType,
    Subnet,
)
from tests.providers.aws.utils import AWS_REGION_US_EAST_1, set_mocked_aws_provider

FIREWALL_ARN = "arn:aws:network-firewall:us-east-1:123456789012:firewall/my-firewall"
FIREWALL_NAME = "my-firewall"
VPC_ID_PROTECTED = "vpc-12345678901234567"
VPC_ID_UNPROTECTED = "vpc-12345678901234568"
POLICY_ARN = "arn:aws:network-firewall:us-east-1:123456789012:firewall-policy/my-policy"


class Test_networkfirewall_multi_az:
    def test_no_networkfirewall(self):
        networkfirewall_client = mock.MagicMock
        networkfirewall_client.provider = set_mocked_aws_provider(
            [AWS_REGION_US_EAST_1]
        )
        networkfirewall_client.region = AWS_REGION_US_EAST_1
        networkfirewall_client.network_firewalls = {}

        aws_provider = set_mocked_aws_provider([AWS_REGION_US_EAST_1])

        with mock.patch(
            "prowler.providers.common.provider.Provider.get_global_provider",
            return_value=aws_provider,
        ):
            with mock.patch(
                "prowler.providers.aws.services.networkfirewall.networkfirewall_multi_az.networkfirewall_multi_az.networkfirewall_client",
                new=networkfirewall_client,
            ):
                # Test Check
                from prowler.providers.aws.services.networkfirewall.networkfirewall_multi_az.networkfirewall_multi_az import (
                    networkfirewall_multi_az,
                )

                check = networkfirewall_multi_az()
                result = check.execute()

                assert len(result) == 0

    def test_networkfirewall_multi_az_disabled(self):
        networkfirewall_client = mock.MagicMock
        networkfirewall_client.provider = set_mocked_aws_provider(
            [AWS_REGION_US_EAST_1]
        )
        networkfirewall_client.region = AWS_REGION_US_EAST_1
        networkfirewall_client.network_firewalls = {
            FIREWALL_ARN: Firewall(
                arn=FIREWALL_ARN,
                name=FIREWALL_NAME,
                region=AWS_REGION_US_EAST_1,
                policy_arn=POLICY_ARN,
                vpc_id=VPC_ID_PROTECTED,
                tags=[],
                encryption_type="CUSTOMER_KMS",
                deletion_protection=False,
                subnet_mappings=[
                    Subnet(
                        subnet_id="subnet-12345678901234567",
                        ip_addr_type=IPAddressType.IPV4,
                    )
                ],
            )
        }
        aws_provider = set_mocked_aws_provider([AWS_REGION_US_EAST_1])

        with mock.patch(
            "prowler.providers.common.provider.Provider.get_global_provider",
            return_value=aws_provider,
        ):
            with mock.patch(
                "prowler.providers.aws.services.networkfirewall.networkfirewall_multi_az.networkfirewall_multi_az.networkfirewall_client",
                new=networkfirewall_client,
            ):
                # Test Check
                from prowler.providers.aws.services.networkfirewall.networkfirewall_multi_az.networkfirewall_multi_az import (
                    networkfirewall_multi_az,
                )

                check = networkfirewall_multi_az()
                result = check.execute()

                assert len(result) == 1
                assert result[0].status == "FAIL"
                assert (
                    result[0].status_extended
                    == f"Network Firewall {FIREWALL_NAME} is not deployed across multiple AZ."
                )
                assert result[0].region == AWS_REGION_US_EAST_1
                assert result[0].resource_id == FIREWALL_NAME
                assert result[0].resource_tags == []
                assert result[0].resource_arn == FIREWALL_ARN

    def test_networkfirewall_multi_az_enabled(self):
        networkfirewall_client = mock.MagicMock
        networkfirewall_client.provider = set_mocked_aws_provider(
            [AWS_REGION_US_EAST_1]
        )
        networkfirewall_client.region = AWS_REGION_US_EAST_1
        networkfirewall_client.network_firewalls = {
            FIREWALL_ARN: Firewall(
                arn=FIREWALL_ARN,
                name=FIREWALL_NAME,
                region=AWS_REGION_US_EAST_1,
                policy_arn=POLICY_ARN,
                vpc_id=VPC_ID_PROTECTED,
                tags=[],
                encryption_type="CUSTOMER_KMS",
                deletion_protection=True,
                subnet_mappings=[
                    Subnet(
                        subnet_id="subnet-12345678901234567",
                        ip_addr_type=IPAddressType.IPV4,
                    ),
                    Subnet(
                        subnet_id="subnet-12345678901234568",
                        ip_addr_type=IPAddressType.IPV4,
                    ),
                ],
            )
        }

        aws_provider = set_mocked_aws_provider([AWS_REGION_US_EAST_1])

        with mock.patch(
            "prowler.providers.common.provider.Provider.get_global_provider",
            return_value=aws_provider,
        ):
            with mock.patch(
                "prowler.providers.aws.services.networkfirewall.networkfirewall_multi_az.networkfirewall_multi_az.networkfirewall_client",
                new=networkfirewall_client,
            ):
                # Test Check
                from prowler.providers.aws.services.networkfirewall.networkfirewall_multi_az.networkfirewall_multi_az import (
                    networkfirewall_multi_az,
                )

                check = networkfirewall_multi_az()
                result = check.execute()

                assert len(result) == 1
                assert result[0].status == "PASS"
                assert (
                    result[0].status_extended
                    == f"Network Firewall {FIREWALL_NAME} is deployed across multiple AZ."
                )
                assert result[0].region == AWS_REGION_US_EAST_1
                assert result[0].resource_id == FIREWALL_NAME
                assert result[0].resource_tags == []
                assert result[0].resource_arn == FIREWALL_ARN