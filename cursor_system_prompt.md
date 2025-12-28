I need to build the MVP for a "Strategic US Market Monitor" application. This is a full-stack application using FastAPI and a simple HTML/JS front-end. The product definition brief is in product_definition_brief.md in the root directory.

1. Core Context & Goal:
At the root of the project, read the background.md file. My goal is to run a workflow that finds external news relevant to this background and do deep dive LLM analysis.

2. Technology & Tools:
You must interact with the AI Builder Student Portal API. The OpenAPI specification is at https://space.ai-builders.com/backend/openapi.json. The API Key is SUPER_MIND_API_KEY in the .env file, you should load it from the .env file using python-dotenv. All AI calls must use the openai SDK, point to the correct base URL, and use the model supermind-agent-v1. The news search should also based on this API.

- **Market Data**: Databento API (documentation: https://databento.com/docs/api-reference-historical?historical=python&live=python&reference=python). API key is in the .env file called DATABENTO_API_KEY. 

3. Backend Implementation: Python + FastAPI

4. Front-End Implementation(HTML/JS): 
Create a simple web interface served by the FastAPI backend. 

5. Add detailed logging to the console. I want to see:
- [Agent] Decided to call tool: [tool name]
- [System] Tool Output: '...'
- [Agent] Final Answer: '...'
This logging is crucial for me to understand the invisible steps.

6. After development finished, create a readme file in the project root, include the project structure, key features and modules. Also include how to install dependencies and run the app.