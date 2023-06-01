# easyNotion API

![easy-notion-API](https://socialify.git.ci/zuo-shi-yun/easy-notion-API/image?description=1&language=1&logo=https%3A%2F%2Fi.postimg.cc%2Ffb52nbP0%2FNotion.png&name=1&theme=Light)

English|[简体中文](README-zh.md)

:muscle: Function Introduction
------------------------------

*   A simpler and faster Notion API wrapper compared to other existing ones.
*   Closes proxies when sending requests.
*   Provides basic CRUD (Create, Read, Update, Delete) operations.

:bangbang: Usage Limitations
----------------------------

*   Only applicable to Notion pages of type "Database - Full page".
*   All column properties in the database, except the title column, must be of type "text".
*   There is no asynchronous version available.

:wrench: Quick Start
--------------------

First, you need to obtain the Token and database\_id for integrating with Notion. To learn how to obtain the Token, please refer to [this link](https://developers.notion.com/docs/getting-started#step-2-share-a-database-with-your-integration). To get the database\_id, check the URL of the database page in the Notion documentation.

python

```python
from easyNotion import easyNotion

db = easyNotion(database_id='database_id', token='token')

# Get the entire table (unprocessed)
table_all = db.getTableAll()

# Get the processed table
table = db.getTable()

# Query a specific column based on the column name
ret = db.queryCol(col="column_name")

# Query rows based on a specific column
row = db.queryRow(col="column_name", content="column_content")

# Get the total number of rows
row_count = db.getRowCnt()

# Insert data
data = {"title": "test_title", "column_name1": "value1", "column_name2": "value2"}
res = db.insert(data=data)

# Update data
res = db.update(col="column_name", content="column_content", update_col="update_column_name", update_content="new_value", isTitle=False)

# Delete data
res = db.delete(col="column_name", content="column_content")

# Close the session
db.closeSession()
```

Class: easyNotion
-----------------

### Constructor

python

```python
def __init__(self, database_id, token)
```

*   Initializes a new instance of the `easyNotion` class.
*   Parameters:
    *   `database_id` (str): The ID of the Notion database.
    *   `token` (str): The API token used to access the Notion API.

### Class Attributes

#### `baseUrl`

*   Type: String
*   Description: The base URL of the API.

#### `database_id`

*   Type: String
*   Description: The ID of the database.

#### `headers`

*   Type: Dictionary
*   Description: Request headers, including Accept, Notion-Version, Content-Type, Authorization, etc.

#### `session`

*   Type: `requests.Session` object
*   Description: Session object used to send HTTP requests.

#### `table`

*   Type: List
*   Description: Processed data table containing all rows from the database.

### Methods

#### `getTableAll()`

python

```python
def getTableAll(self) -> dict
```

*   Retrieves the raw data table from the Notion database.
*   Returns:
    *   JSON object containing all raw data from the database.

#### `getTable()`

python

```python
def getTable(self) -> list
```

*   Retrieves the processed data table from the Notion database.
*   Returns:
    *   List of dictionaries representing the processed data table.
*   Note:
    *   This method internally calls `getTableAll()` to retrieve the raw data and process it to obtain the final data table.

#### `queryCol(col: str) -> list`

python

```python
def queryCol(self, col: str) -> list
```

*   Queries a specific column in the data table and returns its values.
*   Parameters:
    *   `col` (str): Name of the column to query.
*   Returns:
    *   List of strings containing the values in the specified column.

#### `queryRow(col: str, content: str) -> dict`

python

```python
def queryRow(self, col: str, content: str) -> dict
```

*   Queries a row in the data table based on a specific column and its content.
*   Parameters:
    *   `col` (str): Name of the column to search.
    *   `content` (str): Value to search in the specified column.
*   Returns:
    *   Dictionary representing the raw data of the matching row.
*   Note:
    *   If no matching row is found, an empty dictionary `{}` is returned.

#### `getRowCnt() -> int`

python

```python
def getRowCnt(self) -> int
```

*   Retrieves the total number of rows in the data table.
*   Returns:
    *   Integer representing the total number of rows in the table.

#### `insert(data: dict)`

python

```python
def insert(self, data: dict)
```

*   Inserts data into the Notion database.
*   Parameters:
    *   `data` (dict): Data to insert. The first value in the dictionary must correspond to the value of the "title" column.
*   Returns:
    *   Response object of the API request.

#### `update(col: str, content: str, update_col: str, update_content: str, isTitle=False)`

python

```python
def update(self, col: str, content: str, update_col: str, update_content: str, isTitle=False)
```

*   Updates a specific column of a row in the data table.
*   Parameters:
    *   `col` (str): Column used to identify the row.
    *   `content` (str): Content of the specified column used to identify the row.
    *   `update_col` (str): Name of the column to update.
    *   `update_content` (str): New content to update in the specified column.
    *   `isTitle` (bool): Indicates whether the specified column is the title column. Default is `False`. Set to `True` if the column being updated is the title column.
*   Returns:
    *   Response object of the API request.

#### `delete(col: str, content: str)`

python

```python
def delete(self, col: str, content: str)
```

*   Deletes a row from the data table based on a specific column and its content.
*   Parameters:
    *   `col` (str): Name of the column to delete.
    *   `content` (str): Value that identifies the row to delete in the specified column.
*   Returns:
    *   Response object of the API request.

#### `closeSession()`

python

```python
def closeSession(self)
```

*   Closes the session used for API requests.