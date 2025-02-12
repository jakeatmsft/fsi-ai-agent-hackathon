import json
import os
import time
import datetime
import random
import string
from pathlib import Path
import asyncio

from dotenv import load_dotenv

from promptflow.core import tool
from promptflow.core._connection import AzureOpenAIConnection, CustomConnection

from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    AsyncFunctionTool,
    RequiredFunctionToolCall,
    SubmitToolOutputsAction,
    ToolOutput,
    CodeInterpreterTool,
    BingGroundingTool,
    AsyncToolSet,
)
from azure.identity.aio import DefaultAzureCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

from agent_team import AgentTeam
from user_async_functions import user_async_function_tools

load_dotenv('deploy.env')

tracer = trace.get_tracer(__name__)

@tool
@tracer.start_as_current_span(__file__)
async def my_python_tool(deployment_name:str, subject_context:str, bing_grounding_conn:str, question: str) -> str:


    # Load credentials and settings from .env file
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

            
            #generate random team name

            random_name = ''.join(random.choices(string.ascii_lowercase, k=8))
            agent_team = AgentTeam(random_name, project_client=project_client)
            
            Context=subject_context
            CharacterLimit = 1000
            
            DOCS_QUESTION_ANSWER_NAME = "DocsQuestionAnswer"
            DOCS_QUESTION_ANSWER_INSTRUCTIONS = f"""
                    You are a question answerer for {Context} using documentation site.  Use the WebSearch tool to retrieve information to answer the questions from the docs site.
                    Prepend "site:learn.microsoft.com" to any search query to search only the documentation site. 
                    You take in questions from a questionnaire and emit the answers from the perspective of {Context},
                    using documentation from the public web. You also emit links to any websites you find that help answer the questions.
                    Do not address the user as 'you' - make all responses solely in the third person.
                    If you do not find information on a topic, you simply respond that there is no information available on that topic.
                    You will emit an answer that is no greater than {CharacterLimit} characters in length.
                """
            ANSWER_CHECKER_NAME = "AnswerChecker"
            ANSWER_CHECKER_INSTRUCTIONS = f"""
                    You are an answer checker for {Context}. Your responses always start with either the words ANSWER CORRECT or ANSWER INCORRECT.
                    Given a question and an answer, you check the answer for accuracy regarding {Context},
                    using public web sources when necessary. If everything in the answer is true, you verify the answer by responding "ANSWER CORRECT." with no further explanation.
                    You also ensure that the answer is no greater than {CharacterLimit} characters in length.
                    Otherwise, you respond "ANSWER INCORRECT - " and add the portion that is incorrect.
                    You do not output anything other than "ANSWER CORRECT" or "ANSWER INCORRECT - <portion>".
                """
            LINK_CHECKER_NAME = "LinkChecker"
            
            LINK_CHECKER_INSTRUCTIONS = """
                    You are a link checker. Your responses always start with either the words LINKS CORRECT or LINK INCORRECT.
                    Given a question and an answer that contains links, you verify that the links are working and return a non-error response,
                    using public web sources when necessary. If all links are working, you verify the answer by responding "LINKS CORRECT" with no further explanation.
                    Otherwise, for each bad link, you respond "LINK INCORRECT - " and add the link that is incorrect.
                    You do not output anything other than "LINKS CORRECT" or "LINK INCORRECT - <link>".
                """
            MANAGER_NAME = "Manager"
            MANAGER_INSTRUCTIONS = """
                    You are a manager which reviews the question, the answer to the question, and the links.
                    If the answer checker replies "ANSWER INCORRECT", or the link checker replies "LINK INCORRECT," you can reply "reject" and ask the question answerer to correct the answer.
                    Once the question has been answered properly, you can approve the request by just responding "approve".
                    You do not output anything other than "reject" or "approve".
                """
                
            toolset1 = AsyncToolSet()
            toolset1.add(functions)
            toolset1.add(code_interpreter)
            toolset1.add(bing_grounding)

            
            toolset2 = AsyncToolSet()
            toolset2.add(functions)
            toolset2.add(bing_grounding)

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
            await agent_team.assemble_team()
            user_request = (
                question
            )

            response_msg = await agent_team.process_request(request=user_request)

            await agent_team.dismantle_team()
            
            last_message = next(
                (msg for msg in reversed(response_msg) if msg.get("agent") == DOCS_QUESTION_ANSWER_NAME), 
                None
            )
            last_message_text = (
                last_message.get("text")
                if isinstance(last_message, dict) and "text" in last_message
                else "Agent team did not return a response."
            )
            response_history = response_msg if isinstance(response_msg, list) else []
            return {"last_message": last_message_text, "history": response_history}