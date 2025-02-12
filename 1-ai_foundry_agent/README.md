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

1. Enabling Tracing on your AI project. First, Navigate to the tracing tab in your AI project. Select an existing resource from the dropdown or create a new one.
<img width="1260" alt="image" src="https://github.com/user-attachments/assets/cf9d4122-5936-4ba6-9059-f52224043bca" />

2. Download the github files in your local folder by navigating to the link: https://github.com/jakeatmsft/fsi-ai-agent-hackathon
You can extract the files/folders from your zip folder for ease of access in the later stages. 
<img width="1019" alt="image" src="https://github.com/user-attachments/assets/e8294578-9ae8-46d7-befb-b83001b38fe7" />

3. Navigate to prompt flow within your project and click on upload from local.
<img width="1222" alt="image" src="https://github.com/user-attachments/assets/e42088b6-7308-4461-8485-077503a8b040" />


4. From the extracted files/folders, select and upload the "prompt flow" folder under the "1-ai_foundry_agent" folder. Choose the option as "Chat Flow" for the kind of flow. You can also rename your flow under the "folder name".
<img width="1087" alt="image" src="https://github.com/user-attachments/assets/56ed621a-4e74-4c31-a479-659b740a6a90" />


5. Once you have created the flow, update the deploy.env file with your project connection string and bing chat connection key. The deploy.env can be found under the "Files" section. 
<img width="1085" alt="image" src="https://github.com/user-attachments/assets/32e4441e-64f5-481c-a768-34eefc5eb933" />

The project connection string can be found by navigating to "Overview tab" of your project
<img width="1235" alt="image" src="https://github.com/user-attachments/assets/f5ac3b87-c430-4221-befe-2c1349192602" />

The bing chat connection key cab be found by navigating to your bing resource via the azure portal. Go to the overview and then to "Manage Keys". You can grab any one of the key and paste it in the deploy.env file. Click on Save. 
<img width="1126" alt="image" src="https://github.com/user-attachments/assets/d096ad25-5451-459f-9f67-314c5ff9ff89" />


6. Go back to the created flow and update the model parameter with the deployed model name in the file agent_Websearch.py file. The model name can be found in "Models + EndPoints" within the AI project.
<img width="931" alt="image" src="https://github.com/user-attachments/assets/b8abe774-d8c1-4d7f-8acb-422c031deec1" />


7. Now, you are ready to test your agent by starting the compute session and clicking on "Chat" and asking questions.
<img width="1067" alt="image" src="https://github.com/user-attachments/assets/fcb82b81-bef0-41d5-b589-ca1eb07898e6" />

8. If the agent is working successfully, you will be able to see the agents in the "Agents" tab.
<img width="1153" alt="image" src="https://github.com/user-attachments/assets/05fff0b7-dd4e-4dc6-89ee-d3fd8e0f0294" />

9. You can also 'Deploy' the flow by navigating back to your flow from the flow tab.
<img width="1086" alt="image" src="https://github.com/user-attachments/assets/6ace8968-319d-4c1a-8ac3-356fd466988c" />


