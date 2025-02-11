# Basic Agent Setup using Entra Identity

![Bicep Version](https://azurequickstartsservice.blob.core.windows.net/badges/quickstarts/microsoft.azure-ai-agent-service/basic-agent-identity/BicepVersion.svg)

[![Deploy To Azure](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/deploytoazure.svg?sanitize=true)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2Fazure-quickstart-templates%2Fmaster%2Fquickstarts%2Fmicrosoft.azure-ai-agent-service%2Fbasic-agent-identity%2Fazuredeploy.json)

[![Visualize](https://raw.githubusercontent.com/Azure/azure-quickstart-templates/master/1-CONTRIBUTION-GUIDE/images/visualizebutton.svg?sanitize=true)](http://armviz.io/#/?load=https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2Fazure-quickstart-templates%2Fmaster%2Fquickstarts%2Fmicrosoft.azure-ai-agent-service%2Fbasic-agent-identity%2Fazuredeploy.json)

Resources for the hub, project, storage account, and AI Services will be created for you. The AI Services account will be connected to your project/hub and a gpt-4o-mini model will be deployed in the eastus region. A Microsoft-managed key vault will be used by default.

#### Optional 
use an existing AI Services resource by providing the full arm resource id in the parameters file:

- aiServiceAccountResourceId:/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.CognitiveServices/accounts/{serviceName}

If you want to use an existing Azure OpenAI resource, you will need to update the `aiServiceAccountResourceId` and the `aiServiceKind` parameter in the parameters file. The `aiServiceKind` parameter should be set to `AzureOpenAI`.

## Resources

| Provider and type | Description |
| - | - |
| `Microsoft.Resources/resourceGroups` | The resource group all resources get deployed into |
| `Microsoft.Storage/storageAccounts` | An Azure Storage instance associated to the Azure Machine Learning workspace |
| `Microsoft.MachineLearningServices/workspaces` | An Azure AI hub (Azure Machine Learning RP workspace of kind 'hub') |
| `Microsoft.MachineLearningServices/workspaces` | An Azure AI project (Azure Machine Learning RP workspace of kind 'project') |
| `Microsoft.CognitiveServices/accounts` | An Azure AI Services as the model-as-a-service endpoint provider (allowed kinds: 'AIServices' and 'OpenAI') |
| `Microsoft.CognitiveServices/accounts/deployments` | A gpt-4o-mini model is deployed |
`Tags: `