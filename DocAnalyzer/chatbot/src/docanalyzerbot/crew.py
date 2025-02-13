import os
import yaml
from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
from crewai_tools import PDFSearchTool

# BASE_DIR is the directory where this file (crew.py) is located.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@CrewBase
class PDFProcessingCrew:
    """
    Crew for processing PDF documents and generating markdown reports.
    """
    # Build absolute paths to the configuration files.
    agents_config_path = os.path.join(BASE_DIR, "config", "agents.yaml")
    tasks_config_path = os.path.join(BASE_DIR, "config", "tasks.yaml")

    # Default PDF path and user query (update these as needed)
    pdf_path = "/Users/santhisampath/Downloads/fedoc.pdf"
    user_query = "document analysis"  # This will be overridden by the user's input in main.py

    # Initialize the PDF search tool with the appropriate configurations.
    tool = PDFSearchTool(
        config={
            "llm": {
                "provider": "groq",
                "config": {
                    "model": "llama-3.3-70b-versatile",
                },
            },
            "embedder": {
                "provider": "huggingface",
                "config": {
                    "model": "sentence-transformers/all-mpnet-base-v2",
                },
            },
        }
    )

    @before_kickoff
    def prepare_inputs(self, inputs):
        """
        Enriches the inputs before the crew execution starts.
        """
        inputs['pdf_path'] = self.pdf_path
        inputs['user_prompt'] = self.user_query

        # Check if the PDF file exists.
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")
        else:
            file_size = os.path.getsize(self.pdf_path)
            print(f"[DEBUG] PDF file found: {self.pdf_path} (size: {file_size} bytes)")
        # Rely on PDFSearchTool's internal methods to search the document.
        return inputs

    @after_kickoff
    def process_output(self, output):
        """
        Post-processes the output after the crew execution.
        """
        output.raw += "\nProcessed after kickoff."
        return output

    @agent
    def researcher(self) -> Agent:
        """
        Agent for analyzing the PDF and extracting relevant information.
        """
        with open(self.agents_config_path, 'r') as f:
            agents_conf = yaml.safe_load(f)
        return Agent(
            config=agents_conf['researcher'],
            tools=[self.tool],
            verbose=True
        )

    @agent
    def reporting_analyst(self) -> Agent:
        """
        Agent for generating a concise markdown report based on extracted content.
        """
        with open(self.agents_config_path, 'r') as f:
            agents_conf = yaml.safe_load(f)
        return Agent(
            config=agents_conf['reporting_analyst'],
            tools=[self.tool],
            verbose=True
        )

    @task
    def research_task(self) -> Task:
        """
        Task for extracting relevant content from the PDF based on the user query.
        """
        with open(self.tasks_config_path, 'r') as f:
            tasks_conf = yaml.safe_load(f)
        print(f"[DEBUG] Creating research_task with inputs: pdf_path={self.pdf_path}, user_prompt={self.user_query}")
        return Task(
            config=tasks_conf['research_task'],
            agent=self.researcher(),
            tools=[self.tool],
            inputs={
                'pdf_path': self.pdf_path,
                'user_prompt': self.user_query
            }
        )

    @task
    def reporting_task(self) -> Task:
        """
        Task for formulating a markdown report that directly answers the user's query.
        """
        with open(self.tasks_config_path, 'r') as f:
            tasks_conf = yaml.safe_load(f)
        return Task(
            config=tasks_conf['reporting_task'],
            agent=self.reporting_analyst(),
            tools=[self.tool],
            inputs={
                'pdf_path': self.pdf_path,
                'user_prompt': self.user_query
            }
        )

    @crew
    def crew(self) -> Crew:
        """
        Define the crew workflow with agents and tasks executed sequentially.
        """
        return Crew(
            agents=[self.researcher(), self.reporting_analyst()],
            tasks=[self.research_task(), self.reporting_task()],
            process=Process.sequential,
            verbose=True,
        )
