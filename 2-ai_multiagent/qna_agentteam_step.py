# Copyright (c) Microsoft. All rights reserved.
import asyncio, json
from promptflow.core import tool
from promptflow.core._connection import AzureOpenAIConnection, CustomConnection
from datetime import datetime
import asyncio
import time, datetime
import os
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import AsyncFunctionTool, RequiredFunctionToolCall, SubmitToolOutputsAction, ToolOutput
from azure.ai.projects.models import CodeInterpreterTool, AsyncToolSet
from azure.identity.aio import DefaultAzureCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from agent_team import AgentTeam


from user_async_functions import user_async_functions
from pathlib import Path 
import string
import random
from dotenv import load_dotenv

load_dotenv()


os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"] = 'true'
print("tracing settings: ", os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"])

#tracer = trace.get_tracer(__name__)

@tool
#@tracer.start_as_current_span(__file__)
async def my_python_tool(deployment_name:str, subject_context:str, question: str) -> str:


    # Load credentials and settings from .env file
    async with DefaultAzureCredential() as creds:
        async with AIProjectClient.from_connection_string(
            credential=creds, conn_str=os.environ["PROJECT_CONNECTION_STRING"],
        ) as project_client:
            
            application_insights_connection_string = await project_client.telemetry.get_connection_string()
            configure_azure_monitor(connection_string=application_insights_connection_string)
            # Initialize assistant functions
            functions = AsyncFunctionTool(functions=user_async_functions)
            code_interpreter = CodeInterpreterTool()
            
            #generate random team name

            random_name = ''.join(random.choices(string.ascii_lowercase, k=8))
            agent_team = AgentTeam(random_name, project_client=project_client)
            
            Context=subject_context
            CharacterLimit = 1000
            
            def randomize_name(name, random_name):
                return name + '-' + random_name 
            
            DOCS_QUESTION_ANSWER_NAME = randomize_name("DocsQuestionAnswer",random_name)
            DOCS_QUESTION_ANSWER_INSTRUCTIONS = f"""
                    You are a question answerer for {Context} using documentation site.  Use the WebSearch tool to retrieve information to answer the questions from the docs site.
                    Prepend "site:learn.microsoft.com" to any search query to search only the documentation site. 
                    You take in questions from a questionnaire and emit the answers from the perspective of {Context},
                    using documentation from the public web. You also emit links to any websites you find that help answer the questions.
                    Do not address the user as 'you' - make all responses solely in the third person.
                    If you do not find information on a topic, you simply respond that there is no information available on that topic.
                    You will emit an answer that is no greater than {CharacterLimit} characters in length.
                """
            ANSWER_CHECKER_NAME = randomize_name("AnswerChecker",random_name)
            ANSWER_CHECKER_INSTRUCTIONS = f"""
                    You are an answer checker for {Context}. Your responses always start with either the words ANSWER CORRECT or ANSWER INCORRECT.
                    Given a question and an answer, you check the answer for accuracy regarding {Context},
                    using public web sources when necessary. If everything in the answer is true, you verify the answer by responding "ANSWER CORRECT." with no further explanation.
                    You also ensure that the answer is no greater than {CharacterLimit} characters in length.
                    Otherwise, you respond "ANSWER INCORRECT - " and add the portion that is incorrect.
                    You do not output anything other than "ANSWER CORRECT" or "ANSWER INCORRECT - <portion>".
                """
            LINK_CHECKER_NAME = randomize_name("LinkChecker",random_name)
            LINK_CHECKER_INSTRUCTIONS = """
                    You are a link checker. Your responses always start with either the words LINKS CORRECT or LINK INCORRECT.
                    Given a question and an answer that contains links, you verify that the links are working and return a non-error response,
                    using public web sources when necessary. If all links are working, you verify the answer by responding "LINKS CORRECT" with no further explanation.
                    Otherwise, for each bad link, you respond "LINK INCORRECT - " and add the link that is incorrect.
                    You do not output anything other than "LINKS CORRECT" or "LINK INCORRECT - <link>".
                """
            MANAGER_NAME = randomize_name("Manager",random_name)
            MANAGER_INSTRUCTIONS = """
                    You are a manager which reviews the question, the answer to the question, and the links.
                    If the answer checker replies "ANSWER INCORRECT", or the link checker replies "LINK INCORRECT," you can reply "reject" and ask the question answerer to correct the answer.
                    Once the question has been answered properly, you can approve the request by just responding "approve".
                    You do not output anything other than "reject" or "approve".
                """
                
            toolset1 = AsyncToolSet()
            toolset1.add(functions)
            toolset1.add(code_interpreter)
            
            toolset2 = AsyncToolSet()
            toolset2.add(functions)
            
            # Create agent
            agent_team.add_agent(
                model=deployment_name,
                name=DOCS_QUESTION_ANSWER_NAME,
                instructions=DOCS_QUESTION_ANSWER_INSTRUCTIONS,
                toolset = toolset1,
                can_delegate=False,
            )
            
            agent_team.add_agent(
                model=deployment_name,
                name=ANSWER_CHECKER_NAME,
                instructions=ANSWER_CHECKER_INSTRUCTIONS,
                toolset = toolset2,
                can_delegate=False,
            )
            
            agent_team.add_agent(
                model=deployment_name,
                name=LINK_CHECKER_NAME,
                instructions=LINK_CHECKER_INSTRUCTIONS,
                toolset = toolset2,
                can_delegate=False,
            )
            
            #print(f"Created agent, agent ID: {agent.id}")
            agent_team.assemble_team()
            user_request = (
                question
            )

            response_msg = await agent_team.process_request(request=user_request)

            agent_team.dismantle_team()
            
            last_message = next(
                (msg for msg in reversed(response_msg) if msg.get("agent") == DOCS_QUESTION_ANSWER_NAME), 
                None
            )
            return {"last_message": last_message['text'], "history": response_msg}