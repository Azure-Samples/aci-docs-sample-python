import random
import string
import time
import sys
from os import getenv
from azure.common.client_factory import get_client_from_auth_file
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.mgmt.containerinstance.models import (ContainerGroup,
                                                 Container,
                                                 ContainerGroupNetworkProtocol,
                                                 ContainerGroupRestartPolicy,
                                                 ContainerPort,
                                                 EnvironmentVariable,
                                                 IpAddress,
                                                 Port,
                                                 ResourceRequests,
                                                 ResourceRequirements,
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
    resource_group_name = 'aci-rg-' + ''.join(random.choice(string.digits)
                                              for _ in range(6))
    container_group_name = 'aci-' + ''.join(random.choice(string.digits)
                                            for _ in range(6))

    multi_container_group_name = container_group_name + "-multi"
    task_container_group_name = container_group_name + "-task"

    container_image_app = "microsoft/aci-helloworld"
    container_image_sidecar = "microsoft/aci-tutorial-sidecar"
    container_image_taskbased = "microsoft/aci-wordcount"

    # Authenticate the management clients with Azure.
    # Set the AZURE_AUTH_LOCATION environment variable to the full path to an
    # auth file. Generate an auth file with the Azure CLI or Cloud Shell:
    # az ad sp create-for-rbac --sdk-auth > my.azureauth
    auth_file_path = getenv('AZURE_AUTH_LOCATION', None)
    if auth_file_path is not None:
        print("Authenticating with Azure using credentials in file at {0}"
              .format(auth_file_path))

        aciclient = get_client_from_auth_file(
            ContainerInstanceManagementClient)
        resclient = get_client_from_auth_file(ResourceManagementClient)
    else:
        print("\nFailed to authenticate to Azure. Have you set the"
              " AZURE_AUTH_LOCATION environment variable?\n")

    # Create (and then get) a resource group into which the container groups
    # are to be created
    print("Creating resource group '{0}'...".format(resource_group_name))
    resclient.resource_groups.create_or_update(resource_group_name,
                                               {'location': azure_region})
    resource_group = resclient.resource_groups.get(resource_group_name)

    # Demonstrate various container group operations
    create_container_group(aciclient, resource_group, container_group_name,
                           container_image_app)
    create_container_group_multi(aciclient, resource_group,
                                 multi_container_group_name,
                                 container_image_app,
                                 container_image_sidecar)
    run_task_based_container(aciclient, resource_group,
                             task_container_group_name,
                             container_image_taskbased,
                             None)
    list_container_groups(aciclient, resource_group)
    print_container_group_details(aciclient,
                                  resource_group,
                                  multi_container_group_name)

    # Clean up resources
    input("Press ENTER to delete all resources created by this sample: ")
    aciclient.container_groups.delete(resource_group_name,
                                      container_group_name)
    aciclient.container_groups.delete(resource_group_name,
                                      multi_container_group_name)
    aciclient.container_groups.delete(resource_group_name,
                                      task_container_group_name)
    resclient.resource_groups.delete(resource_group_name)


def create_container_group(aci_client, resource_group,
                           container_group_name, container_image_name):
    """Creates a container group with a single container.

    Arguments:
        aci_client {azure.mgmt.containerinstance.ContainerInstanceManagementClient}
                    -- An authenticated container instance management client.
        resource_group {azure.mgmt.resource.resources.models.ResourceGroup}
                    -- The resource group in which to create the container group.
        container_group_name {str}
                    -- The name of the container group to create.
        container_image_name {str}
                    -- The container image name and tag, for example:
                       microsoft\aci-helloworld:latest
    """
    print("Creating container group '{0}'...".format(container_group_name))

    # Configure the container
    container_resource_requests = ResourceRequests(memory_in_gb=1, cpu=1.0)
    container_resource_requirements = ResourceRequirements(
        requests=container_resource_requests)
    container = Container(name=container_group_name,
                          image=container_image_name,
                          resources=container_resource_requirements,
                          ports=[ContainerPort(port=80)])

    # Configure the container group
    ports = [Port(protocol=ContainerGroupNetworkProtocol.tcp, port=80)]
    group_ip_address = IpAddress(ports=ports,
                                 dns_name_label=container_group_name,
                                 type="Public")
    group = ContainerGroup(location=resource_group.location,
                           containers=[container],
                           os_type=OperatingSystemTypes.linux,
                           ip_address=group_ip_address)

    # Create the container group
    aci_client.container_groups.create_or_update(resource_group.name,
                                                 container_group_name,
                                                 group)

    # Get the created container group
    container_group = aci_client.container_groups.get(resource_group.name,
                                                      container_group_name)

    print("Once DNS has propagated, container group '{0}' will be reachable at"
          " http://{1}".format(container_group_name,
                               container_group.ip_address.fqdn))


def create_container_group_multi(aci_client, resource_group,
                                 container_group_name,
                                 container_image_1, container_image_2):
    """Creates a container group with two containers in the specified
       resource group.

    Arguments:
        aci_client {azure.mgmt.containerinstance.ContainerInstanceManagementClient}
                    -- An authenticated container instance management client.
        resource_group {azure.mgmt.resource.resources.models.ResourceGroup}
                    -- The resource group in which to create the container group.
        container_group_name {str}
                    -- The name of the container group to create.
        container_image_1 {str}
                    -- The first container image name and tag, for example:
                       microsoft\aci-helloworld:latest
        container_image_2 {str}
                    -- The second container image name and tag, for example:
                       microsoft\aci-tutorial-sidecar:latest
    """
    print("Creating container group '{0}'...".format(container_group_name))

    # Configure the containers
    container_resource_requests = ResourceRequests(memory_in_gb=2, cpu=1.0)
    container_resource_requirements = ResourceRequirements(
        requests=container_resource_requests)

    container_1 = Container(name=container_group_name + '-1',
                            image=container_image_1,
                            resources=container_resource_requirements,
                            ports=[ContainerPort(port=80)])

    container_2 = Container(name=container_group_name + '-2',
                            image=container_image_2,
                            resources=container_resource_requirements)

    # Configure the container group
    ports = [Port(protocol=ContainerGroupNetworkProtocol.tcp, port=80)]
    group_ip_address = IpAddress(
        ports=ports, dns_name_label=container_group_name, type='Public')
    group = ContainerGroup(location=resource_group.location,
                           containers=[container_1, container_2],
                           os_type=OperatingSystemTypes.linux,
                           ip_address=group_ip_address)

    # Create the container group
    aci_client.container_groups.create_or_update(resource_group.name,
                                                 container_group_name, group)

    # Get the created container group
    container_group = aci_client.container_groups.get(resource_group.name,
                                                      container_group_name)

    print("Once DNS has propagated, container group '{0}' will be reachable at"
          " http://{1}".format(container_group_name,
                               container_group.ip_address.fqdn))


def run_task_based_container(aci_client, resource_group, container_group_name,
                             container_image_name, start_command_line=None):
    """Creates a container group with a single task-based container who's
       restart policy is 'Never'. If specified, the container runs a custom
       command line at startup.

    Arguments:
        aci_client {azure.mgmt.containerinstance.ContainerInstanceManagementClient}
                    -- An authenticated container instance management client.
        resource_group {azure.mgmt.resource.resources.models.ResourceGroup}
                    -- The resource group in which to create the container group.
        container_group_name {str}
                    -- The name of the container group to create.
        container_image_name {str}
                    -- The container image name and tag, for example:
                       microsoft\aci-helloworld:latest
        start_command_line {str}
                    -- The command line that should be executed when the
                       container starts. This value can be None.
    """
    # If a start command wasn't specified, use a default
    if start_command_line is None:
        start_command_line = "python wordcount.py http://shakespeare.mit.edu/romeo_juliet/full.html"

    # Configure some environment variables in the container which the
    # wordcount.py or other script can read to modify its behavior.
    env_var_1 = EnvironmentVariable(name='NumWords', value='5')
    env_var_2 = EnvironmentVariable(name='MinLength', value='8')

    print("Creating container group '{0}' with start command '{1}'"
          .format(container_group_name, start_command_line))

    # Configure the container
    container_resource_requests = ResourceRequests(memory_in_gb=1, cpu=1.0)
    container_resource_requirements = ResourceRequirements(
        requests=container_resource_requests)
    container = Container(name=container_group_name,
                          image=container_image_name,
                          resources=container_resource_requirements,
                          command=start_command_line.split(),
                          environment_variables=[env_var_1, env_var_2])

    # Configure the container group
    group = ContainerGroup(location=resource_group.location,
                           containers=[container],
                           os_type=OperatingSystemTypes.linux,
                           restart_policy=ContainerGroupRestartPolicy.never)

    # Create the container group
    result = aci_client.container_groups.create_or_update(resource_group.name,
                                                          container_group_name,
                                                          group)

    # Wait for the container create operation to complete. The operation is
    # "done" when the container group provisioning state is one of:
    # Succeeded, Canceled, Failed
    while result.done() is False:
        sys.stdout.write('.')
        time.sleep(1)

    # Get the provisioning state of the container group.
    container_group = aci_client.container_groups.get(resource_group.name,
                                                      container_group_name)
    if str(container_group.provisioning_state).lower() == 'succeeded':
        print("\nCreation of container group '{}' succeeded."
              .format(container_group_name))
    else:
        print("\nCreation of container group '{}' failed. Provisioning state"
              "is: {}".format(container_group_name,
                              container_group.provisioning_state))

    # Get the logs for the container
    logs = aci_client.container.list_logs(resource_group.name,
                                          container_group_name,
                                          container.name)

    print("Logs for container '{0}':".format(container_group_name))
    print("{0}".format(logs.content))


def list_container_groups(aci_client, resource_group):
    """Lists the container groups in the specified resource group.

    Arguments:
       aci_client {azure.mgmt.containerinstance.ContainerInstanceManagementClient}
                   -- An authenticated container instance management client.
       resource_group {azure.mgmt.resource.resources.models.ResourceGroup}
                   -- The resource group containing the container group(s).
    """
    print("Listing container groups in resource group '{0}'...".format(
        resource_group.name))

    container_groups = aci_client.container_groups.list_by_resource_group(
        resource_group.name)

    for container_group in container_groups:
        print("  {0}".format(container_group.name))


def print_container_group_details(aci_client, resource_group, container_group_name):
    """Gets the specified container group and then prints a few of its properties and their values.

    Arguments:
        aci_client {azure.mgmt.containerinstance.ContainerInstanceManagementClient}
                    -- An authenticated container instance management client.
        resource_group {azure.mgmt.resource.resources.models.ResourceGroup}
                    -- The name of the resource group containing the container
                       group.
        container_group_name {str}
                    -- The name of the container group whose details should be
                       printed.
    """
    print("Getting container group details for container group '{0}'..."
          .format(container_group_name))

    container_group = aci_client.container_groups.get(resource_group.name,
                                                      container_group_name)
    print("------------------------")
    print("Name:   {0}".format(container_group.name))
    print("State:  {0}".format(container_group.provisioning_state))
    print("FQDN:   {0}".format(container_group.ip_address.fqdn))
    print("IP:     {0}".format(container_group.ip_address.ip))
    print("Region: {0}".format(container_group.location))
    print("Containers:")
    for container in container_group.containers:
        print("  Name:  {0}".format(container.name))
        print("  Image: {0}".format(container.image))
        print("  State: {0}".format(
            container.instance_view.current_state.state))
        print("  ----------")


if __name__ == "__main__":
    main()
