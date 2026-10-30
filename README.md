# FlowCraft AI – Natural Language to Executable Workflow

## 1. Project Overview

FlowCraft AI is an AI-powered application that converts natural-language instructions into structured and executable data-processing workflows.

The application allows users to upload CSV datasets and describe the operations they want to perform using simple English instructions. Instead of manually writing Python code or SQL queries, users can explain their requirements in natural language.

FlowCraft AI uses a Large Language Model (LLM) through the Groq API to interpret user instructions and generate a structured workflow. The generated workflow is validated, displayed for user review, and executed after user approval.

The application also provides data summaries, visualizations, execution reports, and workflow history.

**Main Idea:** Convert natural-language instructions into structured, validated, and executable data-processing workflows without requiring users to write code.

## 2. Problem Statement

Working with CSV datasets often requires programming knowledge and familiarity with data-processing libraries.

Users may need to perform operations such as:

- Removing duplicate records.
- Handling missing values.
- Filtering records based on conditions.
- Validating numerical ranges.
- Grouping and aggregating data.
- Sorting records.
- Generating data reports.

Performing these operations manually can be time-consuming, especially for users who do not have programming experience.

There is a need for a simple application that allows users to describe data-processing requirements in natural language and automatically converts them into executable operations.

## 3. Project Objectives

The main objectives of FlowCraft AI are:

1. To simplify CSV data processing through natural-language instructions.
2. To integrate Large Language Models into a practical data-processing application.
3. To automatically generate structured workflows based on user requirements.
4. To validate workflows before execution.
5. To provide users with an opportunity to review and approve workflows.
6. To execute predefined data-processing operations safely.
7. To provide data visualizations and execution reports.
8. To maintain workflow execution history.

## 4. Proposed Solution

FlowCraft AI provides an interactive web application built using Streamlit.

The user uploads a CSV file and describes the required data-processing operations in natural language.

The Groq API processes the instruction and generates a structured workflow.

The backend validates the generated workflow using predefined schemas and validation rules. The application then presents the workflow to the user for review.

After the user approves the workflow, the backend executes the requested operations using Pandas.

Finally, the application displays the processed dataset, execution results, visualizations, and reports.

## 5. Key Features

### 5.1 CSV Dataset Upload

Users can upload CSV files directly through the application.

The application loads the dataset using Pandas and provides information such as:

- Total number of rows.
- Total number of columns.
- Column names.
- Data types.
- Dataset overview.
- Data quality information.

### 5.2 Sample Datasets

The application provides sample CSV datasets so users can explore its functionality without uploading their own files.

### 5.3 Natural Language Instructions

Users can describe the required data-processing operations using simple English.

Example:

"Remove duplicate records, remove rows containing missing values, and sort the dataset by marks in descending order."

The application sends the instruction for AI-based workflow generation.

### 5.4 AI-Based Workflow Generation

FlowCraft AI integrates the Groq API to interpret natural-language instructions.

The AI generates a structured workflow containing the requested operations and their parameters.

The application uses the generated workflow as structured input rather than executing arbitrary AI-generated Python code.

### 5.5 Workflow Preview

Before execution, users can review the generated workflow.

The preview helps users understand the operations that will be performed on the dataset.

### 5.6 Workflow Validation

The generated workflow is checked against predefined schemas and validation rules.

This helps ensure that the workflow follows the supported structure and operation requirements.

### 5.7 User Approval and Execution

The application provides a review and approval step before executing the workflow.

After approval, the backend executes the supported operations using predefined Python functions.

### 5.8 Data Processing Operations

The project supports the following operations:

| Operation | Description |
|---|---|
| Remove Duplicates | Removes duplicate records from the dataset. |
| Drop Missing Values | Removes rows containing missing values. |
| Filter Rows | Selects records based on specified conditions. |
| Validate Range | Checks whether values satisfy defined range conditions. |
| Group and Aggregate | Groups records and calculates summary values. |
| Sort Rows | Sorts records using selected columns. |
| Generate Report | Produces a data-processing report. |

### 5.9 Data Visualization

The application uses Plotly to display data visualizations.

Visualizations help users understand dataset characteristics and processing results.

### 5.10 Workflow History

The application maintains information about previously executed workflows using SQLite.

History information includes workflow details, execution status, dataset information, and execution logs.

Users can review previous workflows and manage stored history.

## 6. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language. |
| Streamlit | Frontend and interactive web application. |
| Groq API | Large Language Model integration for natural-language workflow generation. |
| Pandas | CSV loading, data manipulation, and processing. |
| Pydantic | Structured workflow schema and data validation. |
| SQLite | Workflow history storage. |
| Plotly | Interactive data visualization. |
| Pytest | Testing and verification. |
| Git and GitHub | Version control and source code management. |

## 7. System Architecture

The application follows a modular architecture that separates the user interface, backend processing, AI integration, data utilities, and persistence.

### Main Architecture Components

**1. Frontend Layer**

Built using Streamlit. It handles user interaction, CSV uploads, workflow previews, approvals, results, and navigation.

**2. AI Integration Layer**

Uses the Groq API to interpret natural-language instructions and generate structured workflow information.

**3. Workflow Management Layer**

Generates, validates, and manages workflow definitions.

**4. Execution Layer**

Executes supported operations using predefined Python functions and Pandas.

**5. Data Utility Layer**

Handles CSV loading, dataset information, and data-quality analysis.

**6. Persistence Layer**

Uses SQLite to store workflow execution history.

### Architecture Flow

User → Streamlit Interface → Natural Language Instruction → Groq API → Structured Workflow → Workflow Validation → User Approval → Workflow Executor → Pandas Operations → Results and Reports → SQLite History

## 8. Project Folder Structure

```text
FlowCraft_AI/
│
├── app.py
│
├── pages/
│
├── components/
│   ├── __init__.py
│   ├── sidebar.py
│   ├── charts.py
│   ├── workflow_preview.py
│   └── workflow_diagram.py
│
├── backend/
│   ├── __init__.py
│   ├── config.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── workflow_generator.py
│   │   ├── workflow_schema.py
│   │   ├── workflow_validator.py
│   │   ├── workflow_executor.py
│   │   └── operations.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py
│   │   └── history_service.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── csv_handler.py
│       └── validators.py
│
├── data/
│   └── sample/
│       ├── student.csv
│       ├── student1.csv
│       └── students.csv
│
├── .streamlit/
│   └── config.toml
│
├── .env.example
├── .gitignore
├── requirements.txt
└── test_operations_manual.py
```

### Explanation of Important Files

**app.py:** Main application entry point. It handles the Streamlit interface and coordinates the application components and backend services.

**components/sidebar.py:** Manages sidebar navigation.

**components/charts.py:** Handles data visualization.

**components/workflow_preview.py:** Displays the generated workflow for user review.

**components/workflow_diagram.py:** Provides workflow diagram visualization.

**backend/config.py:** Manages application configuration and environment settings.

**backend/core/workflow_generator.py:** Handles workflow generation based on user instructions.

**backend/core/workflow_schema.py:** Defines the structured workflow schema.

**backend/core/workflow_validator.py:** Validates generated workflows.

**backend/core/workflow_executor.py:** Coordinates workflow execution.

**backend/core/operations.py:** Contains predefined data-processing operations.

**backend/services/llm_service.py:** Handles communication with the Groq API.

**backend/services/history_service.py:** Manages workflow history using SQLite.

**backend/utils/csv_handler.py:** Handles CSV loading and dataset information.

**backend/utils/validators.py:** Provides data-quality and validation utilities.

**data/sample/:** Contains sample CSV datasets.

**requirements.txt:** Lists Python dependencies required to run the application.

**.env.example:** Provides an example of the environment variable configuration without exposing API credentials.

**.gitignore:** Specifies files and directories that should not be committed to GitHub.

## 9. Working Methodology

The application follows these steps:

### Step 1: Launch the Application

The user opens FlowCraft AI through its Streamlit interface.

### Step 2: Upload a Dataset

The user uploads a CSV file or selects an available sample dataset.

### Step 3: Analyze the Dataset

The application loads the dataset and displays its overview and data-quality information.

### Step 4: Enter Natural Language Instructions

The user describes the required data-processing operations.

Example:

"Remove duplicate student records and sort students based on marks in descending order."

### Step 5: Generate the Workflow

The application sends the instruction to the AI integration service.

The Groq API generates a structured workflow representing the requested operations.

### Step 6: Validate the Workflow

The backend checks the workflow structure and validates supported operations and their parameters.

### Step 7: Preview and Approve

The application displays the generated workflow. The user reviews and approves it before execution.

### Step 8: Execute the Workflow

The backend executes the approved operations using predefined functions and Pandas.

### Step 9: Display Results

The application displays the processed dataset, execution summaries, reports, and visualizations.

### Step 10: Save Workflow History

The application stores relevant workflow and execution information in SQLite for later review.

## 10. AI Integration

FlowCraft AI uses the Groq API to connect with a Large Language Model.

The AI integration enables users to express data-processing requirements without manually writing programming instructions.

The general process is:

1. Receive the user's natural-language instruction.
2. Send the instruction to the configured Groq model.
3. Obtain a structured workflow response.
4. Validate the response using the workflow schema.
5. Pass the validated workflow to the application for preview and approval.

The AI is responsible for interpreting user requirements and generating structured workflow information. Actual data processing is performed by the application's predefined backend operations.

## 11. Workflow Validation and Execution

The project uses structured workflow validation to check generated workflow information.

Pydantic is used to define and validate workflow data structures.

The execution layer uses predefined operations rather than directly executing arbitrary Python code generated by the AI.

This design helps restrict execution to supported operations and gives users an opportunity to review the requested processing steps before execution.

## 12. Database and History Management

FlowCraft AI uses SQLite for workflow history management.

The application stores information related to workflow execution, allowing users to review previously executed workflows.

History management supports reviewing and managing saved workflow records.

The SQLite database is generated locally during application use and is not intended to be committed to the public GitHub repository.

## 13. Installation and Setup

### Prerequisites

Install the following:

- Python.
- Visual Studio Code or another Python editor.
- Git.
- A Groq API key.

### Step 1: Clone the Repository

```bash
git clone https://github.com/bhargav123321/FlowCraft_AI.git
```

### Step 2: Navigate to the Project

```bash
cd FlowCraft_AI
```

### Step 3: Create a Virtual Environment

```bash
python -m venv .venv
```

### Step 4: Activate the Virtual Environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 6: Configure Environment Variables

Create a `.env` file in the project root directory.

Add the configuration expected by the application:

```dotenv
LLM_PROVIDER=groq
GROQ_API_KEY=your_actual_groq_api_key
MODEL_NAME=your_supported_model_name
```

Replace the placeholder values with the actual configuration required by the application.

Do not upload `.env` or API credentials to GitHub.

### Step 7: Run the Application

```bash
streamlit run app.py
```

The application will open in the browser using the local Streamlit address.

## 14. Security Considerations

FlowCraft AI uses predefined backend operations for data processing.

Important security practices include:

- Keeping API credentials in environment variables or Streamlit Secrets.
- Excluding `.env` files from GitHub.
- Validating AI-generated workflow structures.
- Restricting execution to supported operations.
- Requiring user approval before workflow execution.
- Avoiding direct execution of arbitrary AI-generated Python code.

## 15. Future Enhancements

Possible future improvements include:

1. Support for additional file formats such as Excel and JSON.
2. Additional data-cleaning and transformation operations.
3. Advanced visualizations and reporting.
4. Exporting processed datasets in multiple formats.
5. More detailed workflow execution logs.
6. Support for larger datasets.
7. Improved workflow templates.
8. Additional AI-powered data-analysis capabilities.

## 16. Conclusion

FlowCraft AI demonstrates how Artificial Intelligence can simplify data-processing tasks through natural-language interaction.

By combining the Groq API, Python, Streamlit, Pandas, Pydantic, SQLite, and Plotly, the application provides a structured approach to generating, validating, reviewing, and executing data-processing workflows.

The project aims to reduce the need for manual programming in common CSV-processing tasks and make data processing more accessible to users with different levels of technical knowledge.

**Project Name:** FlowCraft AI – Natural Language to Executable Workflow

**GitHub Repository:** https://github.com/bhargav123321/FlowCraft_AI
