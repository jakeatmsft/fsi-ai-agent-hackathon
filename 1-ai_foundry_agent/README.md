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

5. Create a bing grounding resource by navigating back to the Azure Portal and searching "Bing Resources".
<img width="1270" alt="image" src="https://github.com/user-attachments/assets/9b85b3f3-2bec-4dd1-a093-cdc322625d79" />

a. Once you select "Grounding with Bing Search", proceed with filling the required details like selecting your resource group, selecting a basic pricing tier and providing a name.

<img width="503" alt="image" src="https://github.com/user-attachments/assets/be1dc8ee-f544-438b-9a17-743832982868" />

b. Navigate to your Management Center of AI Foundry and click on "New Connection" under connected resources

<img width="1209" alt="image" src="https://github.com/user-attachments/assets/12dbafdf-c6e4-47d9-b054-636e20046489" />

c. Once you click on the "New Connection", select "Grounding with Bing Search"

<img width="1145" alt="image" src="https://github.com/user-attachments/assets/0df2b85e-ccd1-4792-b680-58fb4084582c" />

d. You will see your created resource on the screen as shown below. You can click on "Add Connection" and it will be linked to your project within AI Foundry. 

<img width="864" alt="image" src="https://github.com/user-attachments/assets/1f382c31-2c1e-4301-98aa-9a26537de12c" />



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


5. Once you have created the flow, update the deploy.env file with your project connection string. The deploy.env can be found under the "Files" section. 
<img width="1064" alt="image" src="https://github.com/user-attachments/assets/a1dd9019-9964-41c7-8195-b71f42b327a7" />


The project connection string can be found by navigating to "Overview tab" of your project
<img width="1235" alt="image" src="https://github.com/user-attachments/assets/f5ac3b87-c430-4221-befe-2c1349192602" />


6. Go back to the created flow and update the model parameter with the deployed model name and bing grounding resource name in the file agent_Websearch.py file. The model name can be found in "Models + EndPoints" within the AI project.
<img width="636" alt="image" src="https://github.com/user-attachments/assets/36373758-cb7c-4f6e-b416-1ca78faaab30" />

The bing grounding resource name can be found within your management center of your AI hub
<img width="1268" alt="image" src="https://github.com/user-attachments/assets/10eccd52-fd47-435c-8161-75fda39950ed" />


7. Now, you are ready to test your agent by starting the compute session and clicking on "Chat" and asking questions.
<img width="1253" alt="image" src="https://github.com/user-attachments/assets/fc13de47-cb49-4f3a-a042-bd75408df6e7" />


8. If the agent is working successfully, you will be able to see the agents in the "Agents" tab.
<img width="1153" alt="image" src="https://github.com/user-attachments/assets/05fff0b7-dd4e-4dc6-89ee-d3fd8e0f0294" />

9. You can also 'Deploy' the flow by navigating back to your flow from the flow tab.
<img width="1086" alt="image" src="https://github.com/user-attachments/assets/6ace8968-319d-4c1a-8ac3-356fd466988c" />


