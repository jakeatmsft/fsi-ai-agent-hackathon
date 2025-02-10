# Single Agent Setup

# Pre-Requisites:
1. Before you begin, please ensure you deploy using the link: https://learn.microsoft.com/en-us/azure/ai-services/agents/quickstart
2. Ensure you as a user have the following roles: Storage Blob Data Contributor, Storage File Data Privileged Contributor is assigned to yourself. You can assign these roles by navigating to your project
on Azure Portal and clicking on the Access Control (IAM). 
3. Go to the storage account within your resource group. Click on the overview tab and ensure that storage account key access is "enabled"
4. Create a bing search resource by following the documentation: https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/create-bing-search-service-resource#create-your-bing-resource

Once you are done with these steps, proceed to your AI Project in AI foundry. 

1. Ensure that "Tracing" is enabled. You can check this in "Tracing" tab in your AI project. 
2. Navigate to prompt flow within your project and upload the git files. For single agent only upload the "prompt flow" folder that can be found in the "1-ai_foundry_agent" . Choose the option as "Chat Flow" for the
kind of flow. 
2. Update the deploy.env file with your project connection string and bing chat connection key
3. Update the model parameter with the deployed model name in the file agent_Websearch.py file. The model name can be found in "Models + EndPoints" within the AI project. 
4. Now, you are ready to test your agent by clicking on "Chat" and asking questions. If the agent is working successfully, you will be able to see the agents in the "Agents" tab. 
