import os
from dotenv import load_dotenv
load_dotenv()

from crewai.tools import BaseTool
from crewai_tools import SerperDevTool
from langchain_community.document_loaders import PyPDFLoader

search_tool = SerperDevTool()

class FinancialDocumentTool(BaseTool):
    name: str = "Financial Document Reader"
    description: str = "Reads a financial PDF document and returns cleaned text."

    def _run(self, path: str) -> str:
        try:
            docs = PyPDFLoader(path).load()

            full_report = "\n".join(
                data.page_content.replace("\n\n", "\n")
                for data in docs
            )

            return full_report

        except Exception as e:
            return f"Error reading PDF: {str(e)}"


class InvestmentTool(BaseTool):
    name: str = "Investment Analysis Tool"
    description: str = "Analyzes financial document data and provides investment insights."

    def _run(self, financial_document_data: str) -> str:
        processed_data = financial_document_data.replace("  ", " ")

        return f"Processed data length: {len(processed_data)} characters"


class RiskTool(BaseTool):
    name: str = "Risk Assessment Tool"
    description: str = "Analyzes financial risks from document data."

    def _run(self, financial_document_data: str) -> str:
        return "Risk assessment logic pending implementation."
