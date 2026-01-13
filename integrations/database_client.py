"""
Database Connection and Schema Discovery
"""
from sqlalchemy import create_engine, inspect, MetaData, Table, text
from sqlalchemy.engine import Engine
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseClient:
    """Client for connecting to and querying SQL databases"""

    def __init__(
        self,
        db_type: str,
        host: str,
        port: int,
        database: str,
        username: str,
        password: str,
        **kwargs
    ):
        """
        Initialize database client

        Args:
            db_type: Database type (postgresql, mysql, mssql, sqlite)
            host: Database host
            port: Database port
            database: Database name
            username: Database username
            password: Database password
            **kwargs: Additional connection parameters
        """
        self.db_type = db_type.lower()
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.connection_params = kwargs
        self.engine: Optional[Engine] = None
        self._connect()

    def _build_connection_string(self) -> str:
        """Build database connection string"""
        if self.db_type == "postgresql":
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.db_type == "mysql":
            return f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.db_type == "mssql":
            return f"mssql+pyodbc://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}?driver=ODBC+Driver+17+for+SQL+Server"
        elif self.db_type == "sqlite":
            return f"sqlite:///{self.database}"
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

    def _connect(self):
        """Establish database connection"""
        try:
            connection_string = self._build_connection_string()
            self.engine = create_engine(
                connection_string,
                pool_pre_ping=True,
                echo=False
            )
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"Successfully connected to {self.db_type} database: {self.database}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise

    def test_connection(self) -> bool:
        """Test the database connection"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False

    def get_tables(self) -> List[str]:
        """Get list of all tables in the database"""
        try:
            inspector = inspect(self.engine)
            return inspector.get_table_names()
        except Exception as e:
            logger.error(f"Error fetching tables: {str(e)}")
            raise

    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """
        Get schema information for a specific table

        Args:
            table_name: Name of the table

        Returns:
            Dictionary containing table schema information
        """
        try:
            inspector = inspect(self.engine)
            columns = inspector.get_columns(table_name)
            primary_keys = inspector.get_pk_constraint(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)
            indexes = inspector.get_indexes(table_name)

            schema = {
                "table_name": table_name,
                "columns": [
                    {
                        "name": col["name"],
                        "type": str(col["type"]),
                        "nullable": col["nullable"],
                        "default": col.get("default"),
                        "primary_key": col["name"] in primary_keys.get("constrained_columns", [])
                    }
                    for col in columns
                ],
                "primary_keys": primary_keys.get("constrained_columns", []),
                "foreign_keys": [
                    {
                        "constrained_columns": fk["constrained_columns"],
                        "referred_table": fk["referred_table"],
                        "referred_columns": fk["referred_columns"]
                    }
                    for fk in foreign_keys
                ],
                "indexes": [
                    {
                        "name": idx["name"],
                        "columns": idx["column_names"],
                        "unique": idx["unique"]
                    }
                    for idx in indexes
                ]
            }
            return schema
        except Exception as e:
            logger.error(f"Error fetching schema for table {table_name}: {str(e)}")
            raise

    def get_all_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get schema information for all tables"""
        try:
            tables = self.get_tables()
            schemas = {}
            for table in tables:
                schemas[table] = self.get_table_schema(table)
            return schemas
        except Exception as e:
            logger.error(f"Error fetching all schemas: {str(e)}")
            raise

    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results

        Args:
            query: SQL query to execute
            params: Optional query parameters

        Returns:
            List of dictionaries representing rows
        """
        try:
            with self.engine.connect() as conn:
                if params:
                    result = conn.execute(text(query), params)
                else:
                    result = conn.execute(text(query))

                # Convert to list of dictionaries
                rows = []
                for row in result:
                    rows.append(dict(row._mapping))
                return rows
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            raise

    def fetch_data(
        self,
        table_name: str,
        columns: Optional[List[str]] = None,
        where_clause: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch data from a table

        Args:
            table_name: Name of the table
            columns: List of columns to fetch (None for all)
            where_clause: Optional WHERE clause
            limit: Optional limit on number of rows

        Returns:
            List of dictionaries representing rows
        """
        try:
            # Build query
            cols = ", ".join(columns) if columns else "*"
            query = f"SELECT {cols} FROM {table_name}"

            if where_clause:
                query += f" WHERE {where_clause}"

            if limit:
                query += f" LIMIT {limit}"

            return self.execute_query(query)
        except Exception as e:
            logger.error(f"Error fetching data from {table_name}: {str(e)}")
            raise

    def insert_data(self, table_name: str, data: Dict[str, Any]) -> int:
        """
        Insert data into a table

        Args:
            table_name: Name of the table
            data: Dictionary of column-value pairs

        Returns:
            ID of inserted row (if applicable)
        """
        try:
            columns = ", ".join(data.keys())
            placeholders = ", ".join([f":{key}" for key in data.keys()])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

            with self.engine.connect() as conn:
                result = conn.execute(text(query), data)
                conn.commit()
                return result.lastrowid
        except Exception as e:
            logger.error(f"Error inserting data into {table_name}: {str(e)}")
            raise

    def update_data(
        self,
        table_name: str,
        data: Dict[str, Any],
        where_clause: str,
        where_params: Optional[Dict] = None
    ) -> int:
        """
        Update data in a table

        Args:
            table_name: Name of the table
            data: Dictionary of column-value pairs to update
            where_clause: WHERE clause for update
            where_params: Parameters for WHERE clause

        Returns:
            Number of rows updated
        """
        try:
            set_clause = ", ".join([f"{key} = :{key}" for key in data.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"

            params = {**data, **(where_params or {})}

            with self.engine.connect() as conn:
                result = conn.execute(text(query), params)
                conn.commit()
                return result.rowcount
        except Exception as e:
            logger.error(f"Error updating data in {table_name}: {str(e)}")
            raise

    def bulk_insert(self, table_name: str, data_list: List[Dict[str, Any]]) -> int:
        """
        Bulk insert data into a table

        Args:
            table_name: Name of the table
            data_list: List of dictionaries containing data to insert

        Returns:
            Number of rows inserted
        """
        try:
            if not data_list:
                return 0

            metadata = MetaData()
            table = Table(table_name, metadata, autoload_with=self.engine)

            with self.engine.connect() as conn:
                result = conn.execute(table.insert(), data_list)
                conn.commit()
                return result.rowcount
        except Exception as e:
            logger.error(f"Error bulk inserting data into {table_name}: {str(e)}")
            raise

    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info(f"Closed connection to {self.db_type} database: {self.database}")
