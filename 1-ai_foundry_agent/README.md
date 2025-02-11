# Single Agent Setup

# Pre-Requisites:
1. Before you begin, please ensure you setup your environment using the link: https://learn.microsoft.com/en-us/azure/ai-services/agents/quickstart
   
     a. Choose the "Python (Azure SDK) option 
 
 <img width="539" alt="image" src="https://github.com/user-attachments/assets/f109df4f-baeb-42cd-868a-f50b779e8ed1" />

     b. You can choose a basic or standard setup. We recommend the standard setup. 

  <img width="530" alt="image" src="https://github.com/user-attachments/assets/a1c52c5b-b35f-4eb0-bff0-9f1f048e9d92" />

     c. Once you click on the standard setup, you will be routed to the page below. Here you could create a new resource group for this agent. Once done, click on "Review + Create"

  <img width="467" alt="image" src="https://github.com/user-attachments/assets/28ee43df-ee2e-4adf-9396-6c8c6d75f774" />

  

2. Navigate to your above created resource group and open the storage account.
<img width="1047" alt="image" src="https://github.com/user-attachments/assets/69924cc2-5598-47a7-9cb7-01fa18c22b0d" />

3. Grant yourself "Storage Blob Data Contributor" and "Storage File Data Privileged Contributor" roles. You can assign these roles by navigating to the Access Control (IAM).Then click on "Add role Assignment"
<img width="691" alt="image" src="https://github.com/user-attachments/assets/9c2a0403-ecfa-4385-96d1-2b304bc30180" />

a. When you are on the "Add role Assignment" tab, search "Storage Blob Data Contributor" and click "Next" which can be found at the bottom of the page.
<img width="650" alt="image" src="https://github.com/user-attachments/assets/9d3db545-cc26-438d-a27a-c2033826f386" />

b. Select "user, group or service principal" and click on select memebers to search your email ID. Once done, click on "Review and Assign" found on the bottom of the page. 
<img width="1256" alt="image" src="https://github.com/user-attachments/assets/4bec57f7-b9f3-4972-8140-eb6b9c18fa19" />

Repeat the same steps to grant yourself "Storage File Data Privileged Contributor"

4. Go to the storage account within your resource group. Click on the overview tab and ensure that storage account key access is "enabled"
<img width="990" alt="image" src="https://github.com/user-attachments/assets/f5de96c5-bcc3-43ce-9832-8dc05e59b3d5" />

5. Create a bing search resource by navigating back to the Azure Portal and searching "Bing Resources".
<img width="820" alt="image" src="https://github.com/user-attachments/assets/4443afb6-680b-42e7-855a-92391deff235" />


a. Once you click on Bing Resources, select "Bing Search" and proceed with adding the resource. 

<img width="1246" alt="image" src="https://github.com/user-attachments/assets/fce18dbb-c618-4c03-bf84-ce8edc44678b" />

b. Fill out the details like selecting your resource group and selecting a basic pricing tier. 
<img width="470" alt="image" src="https://github.com/user-attachments/assets/4bd338f4-d4c4-4191-b9d3-279359584dca" />


## Now you are all set to proceed to your project to start the Single Agent Deployments.

1. Ensure that "Tracing" is enabled. You can check this in "Tracing" tab in your AI project. 
2. Navigate to prompt flow within your project and upload the git files. For single agent only upload the "prompt flow" folder that can be found in the "1-ai_foundry_agent" . Choose the option as "Chat Flow" for the
kind of flow. 
2. Update the deploy.env file with your project connection string and bing chat connection key
3. Update the model parameter with the deployed model name in the file agent_Websearch.py file. The model name can be found in "Models + EndPoints" within the AI project. 
4. Now, you are ready to test your agent by clicking on "Chat" and asking questions. If the agent is working successfully, you will be able to see the agents in the "Agents" tab. 
