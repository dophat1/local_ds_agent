import pandas as pd 
import sys
from io import StringIO
import duckdb

def read_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        return df.to_string()
    except FileNotFoundError:
        return f"The {file_path} is invalid, check it again."    


"""
1. Save real terminal → old_out
2. Replace terminal with fake one → sys.stdout = StringIO()
3. Run code → output goes into fake terminal
4. Restore real terminal → sys.stdout = old_out
5. Read fake terminal contents → output.getvalue()
"""

def python_runner(code):
    try:
        old_out = sys.stdout
        output = sys.stdout = StringIO()
        exec(code)
        return output.getvalue()

    
    except Exception as e: 
        return f"There is {e} in the code, check again."
    
    finally:
        sys.stdout = old_out
        

def sql_query(query):
    try:
        result = duckdb.sql(query)
        return str(result)
    except Exception as e:
        return f"There is {e} when trying to query the data, check again."

"""
The agent loop receives this JSON from the LLM:
json
{
    "tool": "csv_reader",
    "input": "data.csv"
}

We need the dictionary to map the input to the tool so the program know which function to call.
"""

tools = {
    "csv_reader": read_csv,
    "python_runner": python_runner,
    "sql_query": sql_query
}