import asyncio
import datetime
import os
import time
from pathlib import Path

from dotenv import load_dotenv

from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (AsyncFunctionTool, 
                                      RequiredFunctionToolCall, 
                                      SubmitToolOutputsAction, 
                                      ToolOutput, 
                                      AsyncToolSet,
                                      CodeInterpreterTool,
                                      BingGroundingTool)
from azure.ai.projects.telemetry.agents import AIAgentsInstrumentor
from azure.identity.aio import DefaultAzureCredential
from azure.monitor.opentelemetry import configure_azure_monitor

from opentelemetry import trace

from promptflow.core import tool

from user_async_functions import user_async_function_tools

load_dotenv('deploy.env')

tracer = trace.get_tracer(__name__)

@tool
@tracer.start_as_current_span(__file__)
async def agent_websearch(question: str, model_deployment: str, bing_grounding_conn: str) -> str:
    async with DefaultAzureCredential() as creds:
        async with AIProjectClient.from_connection_string(
            credential=creds, conn_str=os.environ["PROJECT_CONNECTION_STRING"],
        ) as project_client:
            
            application_insights_connection_string = await project_client.telemetry.get_connection_string()
            configure_azure_monitor(connection_string=application_insights_connection_string)
            
            bing_connection = await project_client.connections.get(connection_name=bing_grounding_conn)
            conn_id = bing_connection.id
            # Initialize assistant functions
            functions = AsyncFunctionTool(functions=user_async_function_tools)
            code_interpreter = CodeInterpreterTool()
            bing_grounding = BingGroundingTool(conn_id)


            toolset = AsyncToolSet()
            toolset.add(functions)
            toolset.add(code_interpreter)
            toolset.add(bing_grounding)

            agent_name = "docs-research-assistant"
            # Try to find an existing agent with the name "my-docs-assistant"
            agents = await project_client.agents.list_agents()
            agent = next((a for a in agents.data if a.name == agent_name), None)

            if agent is None:
                # Create agent if not found, using create_agent from [`project_client.agents.create_agent`](1-ai_foundry_agent/agent_websearch.py)
                agent = await project_client.agents.create_agent(
                    model=model_deployment,
                    name=agent_name,
                    instructions='You are a question answerer using documentation site. Use the WebSearch tool to retrieve information to answer the questions from the docs site. Prepend "site:learn.microsoft.com" to any search query to search only the documentation site. You take in questions from a questionnaire and emit the answers, using documentation from the public web. You also emit links to any websites you find that help answer the questions. Do not address the user; make all responses solely in the third person. If you do not find information on a topic, simply respond that no information is available on that topic. The answer should be no greater than 1000 characters in length.',
                    tools=functions.definitions + code_interpreter.definitions + bing_grounding.definitions
                )
                print(f"Created agent, agent ID: {agent.id}")
            else:
                print(f"Found existing agent: {agent.id}")

            # Create thread for communication
            thread = await project_client.agents.create_thread()
            print(f"Created thread, ID: {thread.id}")

            # Create and send message
            message = await project_client.agents.create_message(
                thread_id=thread.id, role="user", content=f"Current date is {datetime.datetime.now().strftime('%Y-%m-%d')}. {question}"
            )
            print(f"Created message, ID: {message.id}")

            # Create and process agent run in thread with tools
            # [START create_and_process_run]
            run = await project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id, toolset=toolset)
            # [END create_and_process_run]
            print(f"Run finished with status: {run.status}")

            if run.status == "failed":
                print(f"Run failed: {run.last_error}")

            print(f"Run completed with status: {run.status}")

            # Fetch and log all messages
            messages = await project_client.agents.list_messages(thread_id=thread.id)
            print(f"Messages: {messages}")

            for file_path_annotation in messages.file_path_annotations:
                print(f"File Paths:")
                print(f"Type: {file_path_annotation.type}")
                print(f"Text: {file_path_annotation.text}")
                print(f"File ID: {file_path_annotation.file_path.file_id}")
                print(f"Start Index: {file_path_annotation.start_index}")
                print(f"End Index: {file_path_annotation.end_index}")
                file_name = Path(file_path_annotation.text).name
                await project_client.agents.save_file(
                    file_id=file_path_annotation.file_path.file_id, file_name=file_name
                )
                print(f"Saved image file to: {Path.cwd() / file_name}")

            last_message = messages.text_messages[0].text
            response = print_response_with_citations(last_message)
            return response
        
def print_response_with_citations(response):
    """Prints the response value with citations in Markdown format."""
    value = response['value']
    annotations = response.get('annotations', [])

    last_index = 0
    output = ""

    for annotation in annotations:
        if annotation['type'] == 'url_citation':
            start_index = annotation['start_index']
            end_index = annotation['end_index']
            text = annotation['text']
            url = annotation['url_citation']['url']

            output += value[last_index:start_index]
            output += f"[{text}]({url})"
            last_index = end_index

    output += value[last_index:]
    return(output)
            
