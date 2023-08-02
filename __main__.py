"""An Azure RM Python Pulumi program"""

import pulumi
from pulumi import ResourceOptions, Output, Config, export
from typing import Mapping, Any
from pulumi_azure_native import resources, network, managedidentity, authorization, containerservice
from pulumi_azure_native.containerservice import v20230102preview as containerservicev20230102preview

config = Config()
name = "pk-aks-test"
subscription_id = config.require("subscriptionid")
subnet_cidr = config.require("subnetcidr")
vnet_cidr = config.require("vnetcidr")

def id_to_dict(id_output) -> Mapping[str, Any]:
            my_dict = {}
            my_dict[id_output] = {}
            return my_dict

# Create an Azure Resource Group
resource_group = resources.ResourceGroup(name)

vnet = network.VirtualNetwork(
    "vnet",
    address_space=network.AddressSpaceArgs(
        address_prefixes=[vnet_cidr]),
    resource_group_name=resource_group.name,
    opts=ResourceOptions(ignore_changes=["subnets", "etags"]),
)

subnet = network.Subnet(
    "subnet",
    virtual_network_name=vnet.name,
    resource_group_name=resource_group.name,
    address_prefix=subnet_cidr,
)

cluster_identity = managedidentity.UserAssignedIdentity(
            f"{name}-useridentity",
            resource_group_name=resource_group.name,
        )

subnet_role_assignment = authorization.RoleAssignment(
            f"{name}-roleassignment",
            principal_id=cluster_identity.principal_id,
            principal_type="ServicePrincipal",
            scope=subnet.id,
            role_definition_id=Output.concat(
                "/subscriptions/",
                subscription_id,
                "/providers/Microsoft.Authorization/roleDefinitions/4d97b98b-1d4f-4787-a291-c67834d212e7",
            )
        )

cluster = containerservice.ManagedCluster(
            f"{name}-cluster",
            resource_group_name=resource_group.name,
            auto_scaler_profile=containerservice.ManagedClusterPropertiesAutoScalerProfileArgs(
                balance_similar_node_groups="true",
                expander="random",
                max_empty_bulk_delete="10",
                max_graceful_termination_sec="600",
                max_node_provision_time="15m",
                max_total_unready_percentage="45",
                new_pod_scale_up_delay="0s",
                ok_total_unready_count="3",
                scale_down_delay_after_add="10m",
                scale_down_delay_after_delete="10s",
                scale_down_delay_after_failure="3m",
                scale_down_unneeded_time="10m",
                scale_down_unready_time="20m",
                scale_down_utilization_threshold="0.5",
                scan_interval="10s",
                skip_nodes_with_local_storage="true",
                skip_nodes_with_system_pods="false",
            ),
            agent_pool_profiles=[
                containerservice.ManagedClusterAgentPoolProfileArgs(
                    count=2,
                    max_pods=50,
                    mode="System",
                    os_disk_size_gb=30,
                    os_type="Linux",
                    type="VirtualMachineScaleSets",
                    vm_size="Standard_DS3_v2",
                    vnet_subnet_id=subnet.id,
                    name="nodepool",
                )
            ],
            dns_prefix=resource_group.name,
            enable_rbac=True,
            kubernetes_version="1.27.3",
            identity=containerservice.ManagedClusterIdentityArgs(
                type="UserAssigned",
                user_assigned_identities=cluster_identity.id.apply(id_to_dict),
            ),
            service_principal_profile=containerservice.ManagedClusterServicePrincipalProfileArgs(
                client_id="msi"
            ),
            oidc_issuer_profile=containerservicev20230102preview.ManagedClusterOIDCIssuerProfileArgs(
                enabled=True
            ),
            sku=containerservicev20230102preview.ManagedClusterSKUArgs(name="Base", tier="Standard")
        )

aks_cluster_properties = pulumi.Output.all(resource_group.name, cluster.name).apply(
        lambda args: get_managed_cluster(args[0], args[1])
    )

def get_managed_cluster(resource_group_name, resource_name):
    pulumi.log.info("Getting managed cluster information")
    cluster_properties = containerservice.get_managed_cluster(
        resource_group_name=resource_group_name,
        resource_name=resource_name,
    )
    pulumi.log.info("Got managed cluster information")
    return cluster_properties



export("oidc", aks_cluster_properties.oidc_issuer_profile.issuer_url)