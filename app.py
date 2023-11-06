import streamlit as st
import pyodbc as odbc
import pandas as pd
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Streamlit configuration
st.set_page_config(page_title="AdventureWorks Database Query", layout="wide")

# Define a function to establish a database connection
def init_connection():
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={st.secrets['SERVER_NAME']};"
        f"DATABASE={st.secrets['DATABASE_NAME']};UID={st.secrets['USER_NAME']};PWD={st.secrets['PASSWD']}"
    )
    return odbc.connect(connection_string)

# Streamlit sidebar
with st.sidebar:
    st.header("Interact with Database")
    key = st.text_input("Enter your OpenAI API key")
    st.markdown("## About\nWorks with the help of OpenAI")
    st.write("For Reference")
    st.write("[Streamlit](https://streamlit.io/)")
    st.write("[OpenAI](https://platform.openai.com/docs/models)")

# Main function
def main():
    st.header("SQl Chatbot using AdventureWorks Database")

    openai.api_key = key

    # Establish the database connection
    cnxn = init_connection()
    cursor = cnxn.cursor()

    # Get a list of tables in the database
    cursor.execute("SELECT CONCAT(Table_Schema, '.', Table_Name) FROM Information_Schema.Tables")
    tables = cursor.fetchall()
    table_names = [str(table[0]) for table in tables]

    st.write("Connection Established")

    # Display the list of tables for selection
    option = st.selectbox("Select Your Table", table_names)
    st.write("Table Chosen:", option)

    # Extract the table name from the selected option
    selected_table = option.split(".")[1]

    # Fetch the list of columns for the selected table
    cursor.execute(f"SELECT Column_Name FROM Information_Schema.Columns WHERE Table_Name = '{selected_table}'")
    columns = cursor.fetchall()
    column_names = [str(column[0]) for column in columns]

    # Display the columns as radio buttons
    selected_column = st.radio("Columns", column_names)

    # Input field for the natural language query
    query = st.text_input("Write your query")

    if query:
        # Generate SQL query using OpenAI
        prompt = f"Generate an SQL server query to retrieve {query} from the {selected_table} table."
        response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=100)
        generated_query = response.choices[0].text.strip()
        st.write("Generated SQL Query:")
        st.code(generated_query, language="sql")

        # Execute the generated query
        result = cursor.execute(generated_query)
        data = result.fetchall()

        if len(data) > 0:
            field_names = [i[0] for i in cursor.description]
            df = pd.DataFrame(data, columns=field_names)
            st.write("Data:")
            st.write(df)
        else:
            st.write("No data retrieved.")
    
    cursor.close()
    cnxn.close()

if __name__ == '__main__':
    main()
