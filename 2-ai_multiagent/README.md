## Before starting the multi-agent setup, please make sure you have completed all the prerequisites listed in the README.MD file in the 1-ai_foundry_agent directory

## PreRequisites for Multi-Agent

1. Please ensure that you have a "gpt-4o" model deployed in your AI Project. You can check that in the "Models and Endpoints" section.If the model is not deployed, you can deploy it via "Deploy model" on the below screen. 
<img width="803" alt="image" src="https://github.com/user-attachments/assets/d600a4b9-d67f-4fd6-b940-7b22230d5db5" />

## Multi-Agent Build Process

1. Navigate to prompt flow within your AI project to create a new flow. Select the "Upload from local" option.
<img width="1222" alt="image" src="https://github.com/user-attachments/assets/24697d06-b144-47ca-be73-2b83662b1b54" />

2. Once the upload window opens, upload the "prompt flow" folder found in the 2-ai_multiagent (Ensure that you have downloaded the git repository in your local environment: https://github.com/jakeatmsft/fsi-ai-agent-hackathon)
Ensure that you have uploaded the entire "promptflow" folder. 
<img width="1159" alt="image" src="https://github.com/user-attachments/assets/0a12e2d5-71bb-465d-8073-efd92772814b" />


3. As done in the single agent file, update the "deploy.env" file here as well.
<img width="1046" alt="image" src="https://github.com/user-attachments/assets/3c810f78-beb4-440b-8b9a-54a4b1e45c80" />

The project connection string can be found in the "Overview" page of the project
<img width="1166" alt="image" src="https://github.com/user-attachments/assets/9cbb0e5f-b0e6-4c0b-a166-0e122a9b3d99" />

The Bing Search Key can be found under the "Bing Sources" in the Azure Portal. You can use any key for this deployment.
<img width="1130" alt="image" src="https://github.com/user-attachments/assets/103e3174-bbc6-4606-9788-0663326b7ed5" />

4. Once you have made the above updates, you are ready to chat with your data. Make sure the compute session is running before asking your question!
<img width="1057" alt="image" src="https://github.com/user-attachments/assets/5eb9b302-607f-49c6-a2be-7fe18f1a836b" />

5. You can also see your agents in the "Agents" tab
<img width="809" alt="image" src="https://github.com/user-attachments/assets/552c6d8e-19bf-4e2b-8e20-5e13f0b62049" />

Each interaction within user and agent can be found in the "Threads" tab
<img width="1226" alt="image" src="https://github.com/user-attachments/assets/20a4d1df-8e78-4beb-8bce-43e8148c175b" />

6. You can also deploy this flow via "Deploy" button.



