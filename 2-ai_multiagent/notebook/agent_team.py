# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import yaml  # type: ignore
from typing import Any, Dict, Optional, Set, List
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FunctionTool, ToolSet, MessageRole, Agent, AsyncToolSet, AsyncFunctionTool
import asyncio

class _AgentTeamMember:
    """
    Represents an individual agent on a team.

    :param model: The model (e.g. GPT-4) used by this agent.
    :param name: The agent's name.
    :param instructions: The agent's initial instructions or "personality".
    :param toolset: An optional ToolSet with specialized tools for this agent.
    :param can_delegate: Whether this agent has delegation capability (e.g., 'create_task').
                         Defaults to True.
    """

    def __init__(
        self, model: str, name: str, instructions: str, toolset: Optional[AsyncToolSet] = None, can_delegate: bool = True
    ) -> None:
        self.model = model
        self.name = name
        self.instructions = instructions
        self.agent_instance: Optional[Agent] = None
        self.toolset: Optional[AsyncToolSet] = toolset
        self.can_delegate = can_delegate


class _AgentTask:
    """
    Encapsulates a task for an agent to perform.

    :param recipient: The name of the agent who should receive the task.
    :param task_description: The description of the work to be done or question to be answered.
    :param requestor: The name of the agent or user requesting the task.
    """

    def __init__(self, recipient: str, task_description: str, requestor: str) -> None:
        self.recipient = recipient
        self.task_description = task_description
        self.requestor = requestor


class AgentTeam:
    """
    A class that represents a team of agents.

    """

    # Static container to store all instances of AgentTeam
    _teams: Dict[str, "AgentTeam"] = {}

    _project_client: AIProjectClient
    _thread_id: str = ""
    _team_leader: Optional[_AgentTeamMember] = None
    _members: List[_AgentTeamMember] = []
    _tasks: List[_AgentTask] = []
    _team_name: str = ""

    def __init__(self, team_name: str, project_client: AIProjectClient):
        """
        Initialize a new AgentTeam and set it as the singleton instance.
        """
        # Validate that the team_name is a non-empty string
        if not isinstance(team_name, str) or not team_name:
            raise ValueError("Team name must be a non-empty string.")
        # Check for existing team with the same name
        if team_name in AgentTeam._teams:
            raise ValueError(f"A team with the name '{team_name}' already exists.")
        self.team_name = team_name
        if project_client is None:
            raise ValueError("No AIProjectClient provided.")
        self._project_client = project_client
        # Store the instance in the static container
        AgentTeam._teams[team_name] = self

        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the full path to the config file
        file_path = os.path.join(current_dir, "agent_team_config.yaml")
        with open(file_path, "r") as config_file:
            config = yaml.safe_load(config_file)
            self.TEAM_LEADER_INSTRUCTIONS = config["TEAM_LEADER_INSTRUCTIONS"]
            self.TEAM_LEADER_INITIAL_REQUEST = config["TEAM_LEADER_INITIAL_REQUEST"]
            self.TEAM_LEADER_TASK_COMPLETENESS_CHECK_INSTRUCTIONS = config[
                "TEAM_LEADER_TASK_COMPLETENESS_CHECK_INSTRUCTIONS"
            ]
            self.TEAM_MEMBER_CAN_DELEGATE_INSTRUCTIONS = config["TEAM_MEMBER_CAN_DELEGATE_INSTRUCTIONS"]
            self.TEAM_MEMBER_NO_DELEGATE_INSTRUCTIONS = config["TEAM_MEMBER_NO_DELEGATE_INSTRUCTIONS"]
            self.TEAM_LEADER_MODEL = config["TEAM_LEADER_MODEL"].strip()

    @staticmethod
    def get_team(team_name: str) -> "AgentTeam":
        """Static method to fetch the AgentTeam instance by name."""
        team = AgentTeam._teams.get(team_name)
        if team is None:
            raise ValueError(f"No team found with the name '{team_name}'.")
        return team

    @staticmethod
    def _remove_team(team_name: str) -> None:
        """Static method to remove an AgentTeam instance by name."""
        if team_name not in AgentTeam._teams:
            raise ValueError(f"No team found with the name '{team_name}'.")
        del AgentTeam._teams[team_name]

    def add_agent(
        self, model: str, name: str, instructions: str, toolset: Optional[AsyncToolSet] = None, can_delegate: bool = True
    ) -> None:
        """
        Add a new agent (team member) to this AgentTeam.

        :param model: The model name (e.g. GPT-4) for the agent.
        :param name: The name of the agent being added.
        :param instructions: The initial instructions/personality for the agent.
        :param toolset: An optional ToolSet to configure specific tools (functions, etc.)
                        for this agent. If None, we'll create a default set.
        :param can_delegate: If True, the agent can delegate tasks (via create_task).
                            If False, the agent does not get 'create_task' in its ToolSet
                            and won't mention delegation in instructions.
        """
        if toolset is None:
            toolset = AsyncToolSet()

        if can_delegate:
            # If agent can delegate, ensure it has 'create_task'
            try:
                function_tool = toolset.get_tool(AsyncFunctionTool)
                function_tool.add_functions(agent_team_default_functions)
            except ValueError:
                default_function_tool = AsyncFunctionTool(agent_team_default_functions)
                toolset.add(default_function_tool)

        member = _AgentTeamMember(
            model=model,
            name=name,
            instructions=instructions,
            toolset=toolset,
            can_delegate=can_delegate,
        )
        self._members.append(member)

    def _add_task(self, task: _AgentTask) -> None:
        """
        Add a new task to the team's task list.

        :param task: The task to be added.
        """
        self._tasks.append(task)

    async def create_team_leader(self, model: str, name: str, instructions: str, toolset: Optional[AsyncToolSet] = None) -> None:
        """
        Add a new agent (team member) to this AgentTeam.

        If team leader has not been created prior to the call to assemble_team,
        then default team leader will be created automatically.

        :param model: The model name (e.g. GPT-4) for the agent.
        :param name: The name of the team leader agent being.
        :param instructions: The initial instructions/personality for the agent.
        :param toolset: An optional ToolSet to configure specific tools (functions, etc.) for the agent.
        """
        assert self._project_client is not None, "project_client must not be None"
        assert self._team_leader is None, "team leader has already been created"
        # List all agents (will be empty at this moment if you haven't added any, or you can append after they're added)
        for member in self._members:
            instructions += f"- {member.name}: {member.instructions}\n"

        self._team_leader = _AgentTeamMember(
            model=model,
            name=name,
            instructions=instructions,
            toolset=toolset,
            can_delegate=True,
        )
        self._team_leader.agent_instance = await self._project_client.agents.create_agent(
            model=self._team_leader.model,
            name=self._team_leader.name,
            instructions=self._team_leader.instructions,
            toolset=self._team_leader.toolset,
        )

    async def _create_team_leader(self):
        """
        Create and initialize the default 'TeamLeader' agent with awareness of all other agents.
        """
        toolset = AsyncToolSet()
        toolset.add(default_function_tool)
        instructions = self.TEAM_LEADER_INSTRUCTIONS.format(agent_name="TeamLeader", team_name=self.team_name) + "\n"
        await self.create_team_leader(
            model=self.TEAM_LEADER_MODEL,
            name="TeamLeader",
            instructions=instructions,
            toolset=toolset,
        )

    async def assemble_team(self):
        """
        Create the team leader agent and initialize all member agents with
        their configured or default toolsets.
        """
        assert self._project_client is not None, "project_client must not be None"

        if self._team_leader is None:
            await self._create_team_leader()

        for member in self._members:
            if member is self._team_leader:
                continue

            team_description = ""
            for other_member in self._members:
                if other_member != member:
                    team_description += f"- {other_member.name}: {other_member.instructions}\n"

            if member.can_delegate:
                extended_instructions = self.TEAM_MEMBER_CAN_DELEGATE_INSTRUCTIONS.format(
                    name=member.name,
                    team_name=self._team_name,
                    original_instructions=member.instructions,
                    team_description=team_description,
                )
            else:
                extended_instructions = self.TEAM_MEMBER_NO_DELEGATE_INSTRUCTIONS.format(
                    name=member.name,
                    team_name=self._team_name,
                    original_instructions=member.instructions,
                    team_description=team_description,
                )
            member.agent_instance = await self._project_client.agents.create_agent(
                model=member.model, name=member.name, instructions=extended_instructions, toolset=member.toolset
            )

    async def dismantle_team(self) -> None:
        """
        Delete all agents (including the team leader) from the project client.
        """
        assert self._project_client is not None, "project_client must not be None"

        # Handle team leader
        if self._team_leader and self._team_leader.agent_instance:
            if asyncio.iscoroutine(self._team_leader.agent_instance):
                # Await the coroutine and store its result
                self._team_leader.agent_instance = await self._team_leader.agent_instance
            team_leader_instance = self._team_leader.agent_instance
            print(f"Deleting team leader agent '{self._team_leader.name}'")
            await self._project_client.agents.delete_agent(team_leader_instance.id)

        # Handle other team members
        for member in self._members:
            if member is not self._team_leader and member.agent_instance:
                if asyncio.iscoroutine(member.agent_instance):
                    member.agent_instance = await member.agent_instance
                agent_instance = member.agent_instance
                print(f"Deleting agent '{member.name}'")
                await self._project_client.agents.delete_agent(agent_instance.id)

        AgentTeam._remove_team(self.team_name)

    
    async def process_request(self, request: str) -> List[str]:
        """
        Handle a user's request by creating a team and delegating tasks to
        the team leader. The team leader may generate additional tasks.
    
        :param request: The user's request or question.
        :return: A list of text messages from the agent.
        """
        assert self._project_client is not None, "project client must not be None"
        assert self._team_leader is not None, "team leader must not be None"
    
        thread = await self._project_client.agents.create_thread()
        print(f"Created thread with ID: {thread.id}")
        self._thread_id = thread.id
    
        team_leader_request = self.TEAM_LEADER_INITIAL_REQUEST.format(original_request=request)
        self._add_task(_AgentTask(self._team_leader.name, team_leader_request, "user"))
    
        agent_responses = []  # List to store agent text messages
    
        while self._tasks:
            task = self._tasks.pop(0)
            print(
                f"Starting task for agent '{task.recipient}'. "
                f"Requestor: '{task.requestor}'. "
                f"Task description: '{task.task_description}'."
            )
    
            message = await self._project_client.agents.create_message(
                thread_id=self._thread_id,
                role="user",
                content=task.task_description,
            )
            print(f"Created message with ID: {message.id} for task in thread {self._thread_id}")
    
            agent = self._get_member_by_name(task.recipient)
            if agent and agent.agent_instance:
                # Check if agent.agent_instance has been resolved
                if asyncio.iscoroutine(agent.agent_instance):
                    agent_instance = await agent.agent_instance
                    # Replace the coroutine with its result to prevent re-awaiting
                    agent.agent_instance = agent_instance
                else:
                    agent_instance = agent.agent_instance
                print('creating process {}-{}-{}'.format(self._thread_id, agent_instance.id, task.recipient))
                run = await self._project_client.agents.create_and_process_run(
                    thread_id=self._thread_id,
                    assistant_id=agent_instance.id,
                )
                print(f"Created and processed run for agent '{agent.name}', run ID: {run.id}")
    
                messages = await self._project_client.agents.list_messages(thread_id=self._thread_id)
                # text_message = messages.get_last_text_message_by_role(role=MessageRole.AGENT)
                # if text_message and text_message.get("content") and len(text_message["content"]) > 0:
                #     # Extract the text from the first content item.
                #     content_item = text_message["content"][0]

                # else:
                #     print(f"Agent '{agent.name}' completed task but no valid text message was returned.")
                text_message = messages.get_last_text_message_by_role(role=MessageRole.AGENT)
                if text_message and text_message.text:
                    # Use the assistant_id from text_message if available; otherwise fallback to agent_instance.id.
                    assistant_id = text_message.get("assistant_id", agent_instance.id)
                    last_message = {"assistant_id": assistant_id, "text": text_message.text.value, "agent": agent.name}
                    agent_responses.append(last_message)
                    print(f"Agent '{agent.name}' completed task. Outcome: {last_message}")
                    print(f"Agent '{agent.name}' completed task. " f"Outcome: {text_message.text.value}")

                else:
                    print(f"Agent '{agent.name}' completed task but no valid text message was returned.")

                    #if self._current_task_span is not None:
                    #    self._add_task_completion_event(self._current_task_span, result=text_message.text.value)
            # If no tasks remain AND the recipient is not the TeamLeader,
            # let the TeamLeader see if more delegation is needed.
            if not self._tasks and not task.recipient == "TeamLeader":
                team_leader_request = self.TEAM_LEADER_TASK_COMPLETENESS_CHECK_INSTRUCTIONS
                task = _AgentTask(
                    recipient=self._team_leader.name, task_description=team_leader_request, requestor="user"
                )
                self._add_task(task)
        return agent_responses  
                
    def _get_member_by_name(self, name) -> Optional[_AgentTeamMember]:
        """
        Retrieve a team member (agent) by name.
        If no member with the specified name is found, returns None.

        :param name: The agent's name within this team.
        """
        if name == "TeamLeader":
            return self._team_leader
        for member in self._members:
            if member.name == name:
                return member
        return None


def _create_task(team_name: str, recipient: str, request: str, requestor: str) -> str:
    """
    Requests another agent in the team to complete a task.

    :param team_name (str): The name of the team.
    :param recipient (str): The name of the agent that is being requested to complete the task.
    :param request (str): A description of the to complete. This can also be a question.
    :param requestor (str): The name of the agent who is requesting the task.
    :return: True if the task was successfully received, False otherwise.
    :rtype: str
    """
    task = _AgentTask(recipient=recipient, task_description=request, requestor=requestor)
    team: Optional[AgentTeam] = None
    try:
        team = AgentTeam.get_team(team_name)
    except:
        pass
    if team is not None:
        team._add_task(task)
        return "True"
    return "False"

def create_task(team_name: str, recipient: str, request: str, requestor: str) -> str:
    return _create_task(team_name, recipient, request, requestor)


# Any additional functions that might be used by the agents:
agent_team_default_functions: Set = {
    _create_task,
    create_task
}

default_function_tool = AsyncFunctionTool(functions=agent_team_default_functions)

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
            