import tempfile
import csv

import streamlit as st
import pandas as pd

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.duckdb import DuckDbTools
from agno.tools.pandas import PandasTools


def preprocess_file(file):

    try:
        if file.name.endswith(".csv"):
            df = pd.read_csv(
                file,
                encoding="utf-8",
                na_values=["NA", "N/A", "missing"]
            )

        elif file.name.endswith(".xlsx"):
            df = pd.read_excel(
                file,
                na_values=["NA", "N/A", "missing"]
            )

        else:
            st.error("Please upload a CSV or Excel file.")
            return None, None, None

        # Convert date and numeric columns
        for column in df.columns:

            if "date" in column.lower():

                df[column] = pd.to_datetime(
                    df[column],
                    errors="coerce"
                )

            elif df[column].dtype == "object":

                try:
                    df[column] = pd.to_numeric(df[column])

                except (ValueError, TypeError):
                    pass

        # Save temporary CSV for DuckDB
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".csv"
        ) as temp_file:

            temp_path = temp_file.name

            df.to_csv(
                temp_path,
                index=False,
                quoting=csv.QUOTE_ALL
            )

        return temp_path, df.columns.tolist(), df

    except Exception as error:

        st.error(f"Error processing file: {error}")

        return None, None, None


# Streamlit UI

st.set_page_config(
    page_title="AI Data Analysis Agent",
    page_icon="📊"
)

st.title("📊 AI Data Analysis Agent")

st.caption(
    "Upload a CSV or Excel file and ask questions "
    "about your data using natural language."
)


uploaded_file = st.file_uploader(
    "Upload a CSV or Excel file",
    type=["csv", "xlsx"]
)


if uploaded_file:

    temp_path, columns, df = preprocess_file(
        uploaded_file
    )

    if temp_path:

        st.subheader("Uploaded Data")

        st.dataframe(
            df,
            width="stretch"
        )

        st.write(
            "**Columns:**",
            ", ".join(columns)
        )

        # DuckDB
        duckdb_tools = DuckDbTools()

        duckdb_tools.load_local_csv_to_table(
            path=temp_path,
            table="uploaded_data"
        )

        # AI Data Analyst
        data_analyst_agent = Agent(
            name="AI Data Analyst",
            model=Ollama(
                id="qwen2.5:0.5b"
            ),
            tools=[
                duckdb_tools,
                PandasTools()
            ],
            instructions=[
                "You are an expert data analyst.",
                "Use the uploaded_data table to answer questions.",
                "Use DuckDB for filtering, aggregation and calculations.",
                "Use Pandas when useful for data analysis.",
                "Do not invent values.",
                "Clearly explain the results.",
                "Use tables for numerical results when appropriate.",
                "Keep answers concise."
            ],
            markdown=True
        )

        user_query = st.text_area(
            "Ask a question about your data:",
            placeholder=(
                "Example: What is the average sales value?"
            )
        )

        if st.button("Analyze Data"):

            if not user_query.strip():

                st.warning(
                    "Please enter a question."
                )

            else:

                with st.spinner(
                    "Analyzing your data..."
                ):

                    try:

                        response = (
                            data_analyst_agent.run(
                                user_query
                            )
                        )

                        st.subheader(
                            "Analysis Result"
                        )

                        st.markdown(
                            response.content
                        )

                    except Exception as error:

                        st.error(
                            f"Analysis error: {error}"
                        )