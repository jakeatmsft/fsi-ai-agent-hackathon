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
                                      CodeInterpreterTool)
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
async def agent_websearch(question: str, model_deployment: str) -> str:
    async with DefaultAzureCredential() as creds:
        async with AIProjectClient.from_connection_string(
            credential=creds, conn_str=os.environ["PROJECT_CONNECTION_STRING"],
        ) as project_client:
            
            application_insights_connection_string = await project_client.telemetry.get_connection_string()
            configure_azure_monitor(connection_string=application_insights_connection_string)
            
            # Initialize assistant functions
            functions = AsyncFunctionTool(functions=user_async_function_tools)
            code_interpreter = CodeInterpreterTool()

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
                    tools=functions.definitions + code_interpreter.definitions
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

            # Create and run assistant task
            run = await project_client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)
            print(f"Created run, ID: {run.id}")

            # Polling loop for run status
            while run.status in ["queued", "in_progress", "requires_action"]:
                run = await project_client.agents.get_run(thread_id=thread.id, run_id=run.id)

                if run.status == "requires_action" and isinstance(run.required_action, SubmitToolOutputsAction):
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls
                    if not tool_calls:
                        print("No tool calls provided - cancelling run")
                        await project_client.agents.cancel_run(thread_id=thread.id, run_id=run.id)
                        break

                    tool_outputs = []
                    for tool_call in tool_calls:
                        if isinstance(tool_call, RequiredFunctionToolCall):
                            try:
                                output = await functions.execute(tool_call)
                                tool_outputs.append(
                                    ToolOutput(
                                        tool_call_id=tool_call.id,
                                        output=output,
                                    )
                                )
                            except Exception as e:
                                print(f"Error executing tool_call {tool_call.id}: {e}")

                    print(f"Tool outputs: {tool_outputs}")
                    if tool_outputs:
                        await project_client.agents.submit_tool_outputs_to_run(
                            thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
                        )

                print(f"Current run status: {run.status}")

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

            last_message = messages.text_messages[0].text.value
            return last_message
            
