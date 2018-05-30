import random
import string
from os import environ
from azure.common.client_factory import get_client_from_auth_file
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.mgmt.resource import ResourceManagementClient

def main():
   """Main entry point for the application.
   """

   resource_group_name = 'aci-rg-' + ''.join(random.choice(string.digits) for _ in range(6))
   container_group_name = 'aci-' + ''.join(random.choice(string.digits) for _ in range(6))
   multi_container_group_name = container_group_name + "-multi";
   async_container_group_name = container_group_name + "-async";
   task_container_group_name  = container_group_name + "-task";

   container_image_app = "microsoft/aci-helloworld";
   container_image_sidecar = "microsoft/aci-tutorial-sidecar";
   container_image_taskbased = "microsoft/aci-wordcount";

   # Authenticate the management clients with Azure. Set the AZURE_AUTH_LOCATION
   # environment variable to the full path to an auth file. Generate an auth
   # file with the Azure CLI: az ad sp create-for-rbac --sdk-auth > my.azureauth
   try:
       print("Authenticating with Azure using credentials in file at {0}".format(environ['AZURE_AUTH_LOCATION']))

       aciclient = get_client_from_auth_file(ContainerInstanceManagementClient)
       armclient = get_client_from_auth_file(ResourceManagementClient)
   except (EnvironmentError, KeyError):
       print("\nFailed to authenticate to Azure. Have you set the AZURE_AUTH_LOCATION environment variable?\n")
       raise

   # Create a resource group into which the container groups are to be created
   create_resource_group(armclient, resource_group_name, 'eastus')

   # Demonstrate various container group operations
   #create_container_group(aciclient, resource_group_name, container_group_name, container_image_app)
   #create_container_group_multi(aciclient, resource_group_name, multi_container_group_name, container_image_app, container_image_sidecar)
   #create_container_group_with_polling(aciclient, resource_group_name, async_container_group_name, container_image_app)
   #run_task_based_container(aciclient, resource_group_name, task_container_group_name, container_image_taskbased, None)
   list_container_groups(aciclient, resource_group_name)
   #print_container_group_details()

def create_resource_group(resource_client, resource_group_name, azure_region):
    """[summary]

    Arguments:
        resource_client {ResourceManagementClient} -- An authenticated resource management client.
        resource_group_name {string} -- The name of the resource group to be created.
        azure_region {string} -- The Azure region in which to create the resource group.
    """
    print("Creating resource group '{0}'...".format(resource_group_name))

    resource_client.resource_groups.create_or_update(resource_group_name, { 'location': azure_region })




def list_container_groups(client, resource_group_name):
   """Lists the container groups in the specified resource group.

   Arguments:
       client {ContainerInstanceManagementClient} -- An authenticated container group client.
       resource_group_name {str} -- The name of the resource group containing the container group(s).
   """
   print("Listing container groups in resource group '{0}'...".format(resource_group_name))

   container_groups = client.container_groups.list_by_resource_group(resource_group_name)

   for container_group in container_groups:
       print("  {0}".format(container_group.name))

if __name__ == "__main__":
   main()
