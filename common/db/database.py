"""
A module for managing database connections and sessions using SQLAlchemy.

This module provides classes and functions to facilitate database operations,
including creating database engines, session makers, and managing database sessions
in a context manager style.

Classes:
    Database: Represents a database connection with its SQLAlchemy engine and session maker.
    DatabaseManager: Manages multiple database connections and session makers based on database types.

Functions:
    _create_sessionmaker: Creates a SQLAlchemy session maker with specified engine.
    _create_engine: Creates a SQLAlchemy engine with the provided URL.

Context Managers:
    get_session: Context manager that provides a session from a specified database type ('main', 'active', 'history').
                 It handles session creation, commit, rollback on exception, and session closure.

"""

from contextlib import contextmanager
from typing import Literal, Generator

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

from common.environ import Environ
from sqlalchemy import text


class Database:
    """
    Represents a database connection.

    Attributes:
        engine (Engine): The SQLAlchemy engine for database connection.
        sessionmaker (sessionmaker): SQLAlchemy session maker for creating sessions.
    """

    def __init__(self, url: str):
        """
        Initializes the Database instance.

        Args:
            url (str): The URL for connecting to the database.
        """
        self.engine = create_engine(url, connect_args={"check_same_thread": False})
        self.sessionmaker = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )


def _create_sessionmaker(engine: Engine):
    """
    Creates a SQLAlchemy session maker with specified engine.

    Args:
        engine (Engine): The SQLAlchemy engine to bind to the session maker.

    Returns:
        sessionmaker: SQLAlchemy session maker.
    """
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _create_engine(url: str) -> Engine:
    """
    Creates a SQLAlchemy engine with the provided URL.

    Args:
        url (str): The URL for connecting to the database.

    Returns:
        Engine: SQLAlchemy engine.
    """
    return create_engine(url, connect_args={"check_same_thread": False})


class DatabaseManager:
    """
    Manages multiple database connections and session makers based on database types.

    Attributes:
        active_db (Engine): SQLAlchemy engine for the 'active' database.
        history_db (Engine): SQLAlchemy engine for the 'history' database.
        main_db (Engine): SQLAlchemy engine for the 'main' database.
        active_sessionmaker (sessionmaker): SQLAlchemy session maker for 'active' database.
        history_sessionmaker (sessionmaker): SQLAlchemy session maker for 'history' database.
        main_sessionmaker (sessionmaker): SQLAlchemy session maker for 'main' database.
    """

    def __init__(self, neuron_type: str, subtensor_network: str):
        """
        Initializes the DatabaseManager instance.

        Args:
            neuron_type (str): Type of neuron.
            subtensor_network (str): Name of the subtensor network.
        """
        subtensor_network = (
            "finney" if "test" != subtensor_network else subtensor_network
        )
        self.active_db = _create_engine(
            Environ.DB_URL_TEMPLATE.format(
                name=f"{neuron_type}_active", network=subtensor_network
            )
        )
        # Define the SQL queries
        sql_statements = [
            "DELETE FROM order_queue;",
            """
        update bitads_data 
          set sale_date = null, 
              refund = 0,
              sales = 0,
              sale_amount = 0.0,
              order_info = null,
              refund = 0,
              sales_status = 'NEW',
              validator_block = null,
              validator_hotkey = null;
            """,
        ]

        # Establish a connection and execute the queries
        try:
            with self.active_db.connect() as connection:
                for statement in sql_statements:
                    connection.execute(
                        text(statement)
                    )  # Use 'text()' to handle plain SQL queries
                    connection.commit()  # Commit the transaction
        except Exception as ex:
            bt.logging.exception("Error on sql")

        self.history_db = _create_engine(
            Environ.DB_URL_TEMPLATE.format(
                name=f"{neuron_type}_history", network=subtensor_network
            )
        )
        self.main_db = _create_engine(
            Environ.DB_URL_TEMPLATE.format(name=f"main", network=subtensor_network)
        )
        self.active_sessionmaker = _create_sessionmaker(self.active_db)
        self.history_sessionmaker = _create_sessionmaker(self.history_db)
        self.main_sessionmaker = _create_sessionmaker(self.main_db)

    @contextmanager
    def get_session(
        self, db_type: Literal["main", "active", "history"]
    ) -> Generator[Session, None, None]:
        """
        Provides a context manager for retrieving sessions from specific database types.

        Args:
            db_type (Literal["main", "active", "history"]): Type of database to retrieve session for.

        Yields:
            Session: A SQLAlchemy session object.

        Raises:
            ValueError: If an invalid db_type is provided.

        """
        session_maker = getattr(self, f"{db_type}_sessionmaker")
        if not session_maker:
            raise ValueError("Invalid db_type. Must be 'main', 'active', or 'history'.")
        session = session_maker()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
