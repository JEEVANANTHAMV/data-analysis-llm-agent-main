from typing import List, Dict, Any
from pydantic import BaseModel, Field, ValidationError

class ColumnSchema(BaseModel):
    """
    Represents a column in a database table.
    """
    name: str = Field(..., description="The name of the column.")
    data_type: str = Field(..., description="The data type of the column.")

class TableSchema(BaseModel):
    """
    Represents a table in a database schema.
    """
    name: str = Field(..., description="The name of the table.")
    columns: List[ColumnSchema] = Field(..., description="The columns in the table.")

class DatabaseSchema(BaseModel):
    """
    Represents the entire database schema.
    """
    tables: List[TableSchema] = Field(..., description="The list of tables in the database schema.")

    @classmethod
    def from_response(cls, raw_schema: List[Dict[str, Any]]) -> "DatabaseSchema":
        """
        Parse a raw schema response into a structured DatabaseSchema object.
        """
        tables_dict = {}
        for row in raw_schema:
            table_name = row["table_name"]
            column = ColumnSchema(name=row["column_name"], data_type=row["data_type"])
            if table_name not in tables_dict:
                tables_dict[table_name] = []
            tables_dict[table_name].append(column)

        tables = [TableSchema(name=table, columns=columns) for table, columns in tables_dict.items()]
        return cls(tables=tables)

class QueryResult(BaseModel):
    """
    Represents the results of an executed query.
    """
    columns: List[str] = Field(..., description="List of column names in the result set.")
    data: List[Dict[str, Any]] = Field(..., description="List of rows in the result set.")

    @classmethod
    def from_raw_results(cls, raw_results: List[Dict[str, Any]]) -> "QueryResult":
        """
        Parse raw query results into a structured QueryResult object.
        """
        if not raw_results:
            return cls(columns=[], data=[])
        columns = list(raw_results[0].keys())
        return cls(columns=columns, data=raw_results)

class VisualizationConfig(BaseModel):
    """
    Represents the configuration for a visualization.
    """
    x: str = Field(..., description="The column to use for the x-axis.")
    y: str = Field(..., description="The column to use for the y-axis.")
    title: str = Field(..., description="The title of the chart.")
    type: str = Field(..., description="The type of chart (e.g., 'bar', 'line', 'scatter').")