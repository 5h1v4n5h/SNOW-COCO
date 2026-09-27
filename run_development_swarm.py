import asyncio
import os
from agency_swarm import Agent, Agency, ModelSettings

# Load the leaked Fable 5.1 system prompt to be used as shared instructions
fable_prompt_path = os.path.join("system_prompts_leaks", "Anthropic", "claude-fable-5.1.md")
with open(fable_prompt_path, "r", encoding="utf-8") as f:
    fable_prompt = f.read()

# Define the CEO / Project Manager
pm = Agent(
    name="ProjectManager",
    description="Responsible for task planning, management, and breaking down the Enterprise Pharma Copilot into actionable steps.",
    instructions="You are the Project Manager. Use the Fable system prompt guidelines for high efficiency. You communicate with the user and delegate tasks to the Architect and Developer to build the Enterprise Pharma Copilot using React, Docker, and SPCS.",
    model="gpt-4o",
    model_settings=ModelSettings(
        max_tokens=16384,
    )
)

# Define the Architect
architect = Agent(
    name="Architect",
    description="Responsible for designing the system architecture, specifically the React + Docker + FastAPI on SPCS architecture.",
    instructions="You are the Software Architect. You design the SPCS (Snowpark Container Services) architecture for the Enterprise Pharma Copilot. You must use the Fable system prompt guidelines for deep reasoning and system design.",
    model="gpt-4o",
    model_settings=ModelSettings(
        max_tokens=16384,
    )
)

# Define the Developer
developer = Agent(
    name="Developer",
    description="Responsible for writing code, setting up the React frontend, and building the FastAPI backend.",
    instructions="You are the Senior Developer. You write production-grade code for the React UI and FastAPI backend. Use the Fable system prompt guidelines for coding style, safety, and efficiency.",
    model="gpt-4o",
    model_settings=ModelSettings(
        max_tokens=16384,
    )
)

# Initialize the Agency with the Fable prompt as shared instructions
agency = Agency(
    [
        pm,
        [pm, architect],
        [pm, developer],
        [architect, developer]
    ],
    shared_instructions=fable_prompt_path,
)

if __name__ == "__main__":
    print("Starting the Enterprise Pharma Copilot Development Swarm...")
    
    # We ask the agents to plan and develop the project
    async def main():
        prompt = (
            "We are building the Enterprise Pharma Copilot. "
            "Please plan the service architecture using React and FastAPI to be hosted on Snowpark Container Services (SPCS). "
            "Start by providing a comprehensive multi-agent development plan."
        )
        print(f"User: {prompt}")
        response = await agency.get_response(prompt)
        print(f"Agency: {response.final_output}")

    asyncio.run(main())
