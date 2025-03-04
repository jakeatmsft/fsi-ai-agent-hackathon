
from promptflow.core import tool
from promptflow.connections import AzureOpenAIConnection, CustomConnection

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
# Autonomously complete a coding task:
import asyncio
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_ext.teams.magentic_one import MagenticOne
from autogen_agentchat.ui import Console

@tool
async def mag1_tool(input1: str, model_deployment:str, conn:AzureOpenAIConnection) -> str:
    client = AzureOpenAIChatCompletionClient(
            azure_deployment=model_deployment,
            model=model_deployment,
            api_version="2024-06-01",
            azure_endpoint=conn.api_base,
            api_key=conn.api_key
    )
    m1 = MagenticOne(client=client)
    task = input1
    result = await Console(m1.run_stream(task=task+'\nSave all code artifacts, screenshots, and images to a folder named "artifacts"'))
    print(result.messages[-1].content)
    last_msg = result.messages[-1].content
    return last_msg