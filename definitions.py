class Sheet:
    """
    represented xlsx sheet, in memory (more efficient than reading each time from the file)
    """
    def __init__(self, name):
        self.sheet_name = name
        self.sheet_raw = ''

class Table:
    """
    represent the table before it is parsed to be in the database
    """
    def __init__(self):
        self.name = ''
        self.columns = []
        self.comment = ''
        # list to hold constraints which are span on more than one column
        self.multi_columns_unique = []

class TableColumn:
    """
        represent one column in a table
    """
    def __init__(self):
        self.name = ''
        self.data_type = ''
        self.is_nullable = ''
        self.identity = ''
        self.constraint = ''
        self.default_value = ''
        self.is_indexed = ''
        self.comment = ''
        self.foreign_key = ''
        self.cache = ''
