import abc

# abstract class (interface) that is used to create SQL-specific subclasses
# noinspection PyPep8Naming
class SQL_DBMS(abc.ABC):
    # enforce implementing properties and methods in subclassesF
    @property
    @abc.abstractmethod
    def reserved_keywords(self):
        raise NotImplementedError()

    file_header_extra = ''

    @staticmethod
    @abc.abstractmethod
    def build_insert_query(table_name: str, columns_names: str, values: list):
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def build_delete_query(table_name: str, columns_names: str, values: list):
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def create_ddl_queries():
        raise NotImplementedError()
