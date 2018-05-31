# Azure Container Instances Python code samples for documentation

This sample application demonstrates several common [Azure Container Instances](https://docs.microsoft.com/azure/container-instances/) operations in Python using the [Azure libraries for Python](https://docs.microsoft.com/python/azure/python-sdk-azure-overview).

The code in this project is ingested into one or more articles on [docs.microsoft.com](https://docs.microsoft.com). Modifying the code in the sample source may impact the rendering of code snippets on [docs.microsoft.com](https://docs.microsoft.com).

This sample has been tested as functional on Python versions 2.7.15rc1 and 3.6.5.

## Features

The code in this sample project demonstrates the following operations:

* Authenticate with Azure
* Create resource group
* Create single- and multi-container container groups
  * Expose application container to internet with public DNS name
  * Multi-container group includes both application and sidecar containers
  * Run a task-based container with custom command line and environment variables
* List container groups in resource group
* Get and print container group details
* Delete container groups
* Delete resource group

## Getting Started

### Prerequisites

* [Azure subscription](https://azure.microsoft.com/free)
* [Python](https://docs.microsoft.com/python/azure/python-sdk-azure-install#where-to-get-python)
* [pip](https://pypi.org/project/pip/)
* [virtualenv](https://virtualenv.pypa.io) (optional)

### Run the sample

1. Optional but recommended, use [virtualenv](https://virtualenv.pypa.io/en/stable/) to create and activate a virtual environment for the project:
   ```
   virtualenv ~/venv/aci-docs-sample-python
   source ~/venv/aci-docs-sample-python/bin/activate
   ```

1. Use the [Azure CLI](https://docs.microsoft.com/cli/azure) (or [Cloud Shell](https://shell.azure.com/)) to generate an Azure credentials file ([more authentication details](https://docs.microsoft.com/python/azure/python-sdk-azure-authenticate?view=azure-python#mgmt-auth-file))

   `az ad sp create-for-rbac --sdk-auth > my.azureauth`

1. Set environment variable `AZURE_AUTH_LOCATION` to the full path of the credentials file
1. `git clone https://github.com/Azure-Samples/aci-docs-sample-python`
1. `cd aci-docs-sample-python`
1. `pip install -r src/requirements.txt`
1. `python src/aci_docs_sample.py`

   ...sample runs...

1. Exit virtualenv (if using a virtual environment): `deactivate`

## Resources

* [Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python) (GitHub)
* [More Azure Container Instances code samples](https://azure.microsoft.com/resources/samples/?sort=0&term=aci)
