import json
from llm import call_llm
from tools import tools
import os

SYSTEM_PROMPT = """
You are an expert Data Scientist. Your goal is to analyze data and answer the user's questions accurately using your available tools.

### AVAILABLE TOOLS
1. `csv_reader`: Use this tool when the user uploads a CSV file to inspect its structure and content.
2. `python_runner`: Use this tool to execute Python code for data manipulation, statistical analysis, or visualization.
3. `sql_query`: Use this tool to execute database queries to retrieve or aggregate structured data.

### INTERACTION PROTOCOL

Whenever you need to invoke a tool, respond with ONLY a single raw JSON object — 
no prose before or after it, no markdown fences, no explanations.

The "input" field must be valid JSON: encode multi-line code as a single string 
with \\n for newlines (NOT Python triple-quoted strings).

Example of a correctly formatted response:
{"tool": "python_runner", "input": "fibonacci = [0, 1]\\nfor i in range(2, 8):\\n    fibonacci.append(fibonacci[-1] + fibonacci[-2])\\nprint(fibonacci[7])"}

If you want to explain your reasoning, do it BEFORE deciding to call a tool, 
in a separate turn — never mix prose and JSON in the same response.

#### Phase 2: Final Answer (Plain Text)
Once you have collected enough information from the tool outputs to comprehensively answer the user's question, you must transition out of JSON mode. Respond in clear, professional plain text with your final analysis and answer. Do not use the JSON format for your final response.
"""

messages = []

messages.append(
    {
        'role': 'system',
        'content': SYSTEM_PROMPT
    }
)

user_prompt = input("How can I help you ?")

user_file_path = input("Provide me the file path of your data.")

message = {
    'role':'user', 
    'content': user_prompt
}
messages.append(message)

file_path = {
    'role':'user', 
    'content': user_file_path
}


# Only check if user's input is non empty, read_csv do the rest.
if user_file_path:
    messages.append(file_path)



while True:

    llm_output = call_llm(messages)
    messages.append(
        {
            'role':'assistant',
            'content':llm_output
        }
    )

    # Clean the llm output before feed in
    cleaned_output = llm_output.replace('```json', '').replace('```', '')

    try:
        parsed = json.loads(cleaned_output)
        if isinstance(parsed, dict):
            tool_name = parsed['tool']
            tool_function = tools[tool_name]
            result = tool_function(parsed['input'])
            messages.append(
                {
                    'role':'user',
                    'content': result
                }
            )
        else:
            print(cleaned_output)
            break

    except json.JSONDecodeError:
        print(cleaned_output)
        break

    except KeyError:
        messages.append(
            {
                'role':'user',
                'content':f"You have called the wrong in {tool_name}, there are only the following tools that you can call {tools.keys()}"

            } 
        )