import random
import string
import time
from os import environ
from azure.common.client_factory import get_client_from_auth_file
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import ResourceGroup
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.mgmt.containerinstance.models import (ContainerGroup,
                                                 Container,
                                                 ContainerPort,
                                                 Port,
                                                 IpAddress,
                                                 ResourceRequirements,
                                                 ResourceRequests,
                                                 ContainerGroupNetworkProtocol,
                                                 OperatingSystemTypes)

# Support input() on Python 2.x
try:
    input = raw_input
except NameError:
    pass

def main():
    """Main entry point for the application.
    """

    azure_region = 'eastus'
    resource_group_name = 'aci-rg-' + ''.join(random.choice(string.digits) for _ in range(6))
    container_group_name = 'aci-' + ''.join(random.choice(string.digits) for _ in range(6))

    multi_container_group_name = container_group_name + "-multi";
    async_container_group_name = container_group_name + "-async";
    task_container_group_name  = container_group_name + "-task";

    container_image_app = "microsoft/aci-helloworld";
    container_image_sidecar = "microsoft/aci-tutorial-sidecar";
    container_image_taskbased = "microsoft/aci-wordcount";

    # Authenticate the management clients with Azure.
    # Set the AZURE_AUTH_LOCATION environment variable to the full path to an
    # auth file. Generate an auth file with the Azure CLI or Cloud Shell:
    # az ad sp create-for-rbac --sdk-auth > my.azureauth
    try:
        print("Authenticating with Azure using credentials in file at {0}".format(environ['AZURE_AUTH_LOCATION']))

        aciclient = get_client_from_auth_file(ContainerInstanceManagementClient)
        resclient = get_client_from_auth_file(ResourceManagementClient)
    except (IOError, EnvironmentError, KeyError):
        print("\nFailed to authenticate to Azure. Have you set the AZURE_AUTH_LOCATION environment variable?\n")
        raise

    # Create a resource group into which the container groups are to be created
    print("Creating resource group '{0}'...".format(resource_group_name))
    resclient.resource_groups.create_or_update(resource_group_name, { 'location': azure_region })
    resource_group = resclient.resource_groups.get(resource_group_name)

    # Demonstrate various container group operations
    create_container_group(aciclient, resource_group, container_group_name, container_image_app)
    #create_container_group_multi(aciclient, resource_group, multi_container_group_name, container_image_app, container_image_sidecar)
    #run_task_based_container(aciclient, resource_group, task_container_group_name, container_image_taskbased, None)
    list_container_groups(aciclient, resource_group)
    #print_container_group_details()

    input("Press ENTER to delete all resources created by this sample: ")
    resclient.resource_groups.delete(resource_group_name)

def create_container_group(aci_client, resource_group, container_group_name, container_image_name):
    """Creates a container group with a single container.

    Arguments:
        aci_client {azure.mgmt.containerinstance.ContainerInstanceManagementClient} -- An authenticated container instance management client.
        resource_group {azure.mgmt.resource.resources.models.ResourceGroup} -- The resource group in which to create the container group.
        container_group_name {str} -- The name of the container group to create.
        container_image_name {str} -- The container image name and tag, for example 'microsoft\aci-helloworld:latest'.
    """
    print("Creating container group '{0}'...".format(container_group_name))

    # Configure the container
    container_resource_requests = ResourceRequests(memory_in_gb = 1, cpu = 1.0)
    container_resource_requirements = ResourceRequirements(requests = container_resource_requests)
    container = Container(name = container_group_name,
                          image = container_image_name,
                          resources = container_resource_requirements,
                          ports = [ContainerPort(port=80)])

    # Configure the container group
    group_os_type = OperatingSystemTypes.linux
    group_ip_address = IpAddress(ports = [Port(protocol=ContainerGroupNetworkProtocol.tcp,
                                 port = 80)],
                                 dns_name_label = container_group_name)
    group = ContainerGroup(location = resource_group.location,
                           containers = [container],
                           os_type = group_os_type,
                           ip_address = group_ip_address)

    # Create the container group
    aci_client.container_groups.create_or_update(resource_group.name, container_group_name, group)

    # Get the created container group
    container_group = aci_client.container_groups.get(resource_group.name, container_group_name)

    print("Once DNS has propagated, container group '{0}' will be reachable at http://{1}".format(container_group_name, container_group.ip_address.fqdn))

def list_container_groups(aci_client, resource_group):
   """Lists the container groups in the specified resource group.

   Arguments:
       aci_client {azure.mgmt.containerinstance.ContainerInstanceManagementClient} -- An authenticated container instance management client.
       resource_group {azure.mgmt.resource.resources.models.ResourceGroup} -- The resource group containing the container group(s).
   """
   print("Listing container groups in resource group '{0}'...".format(resource_group.name))

   container_groups = aci_client.container_groups.list_by_resource_group(resource_group.name)

   for container_group in container_groups:
       print("  {0}".format(container_group.name))

if __name__ == "__main__":
   main()
