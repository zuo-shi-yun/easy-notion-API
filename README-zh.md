# easyNotion API

![easy-notion-API](https://socialify.git.ci/zuo-shi-yun/easy-notion-API/image?description=1&language=1&logo=https%3A%2F%2Fi.postimg.cc%2Ffb52nbP0%2FNotion.png&name=1&theme=Light)

[English](README.md)|简体中文

## :muscle:功能介绍

- 相较于其他封装的API使用起来更加简单快速的notionAPI
- 发送requests时关闭代理
- 具备基本的增删改查功能

## :bangbang:使用限制

- 只可用于notion中页面类型为"Database - Full page"的页面
- 数据库中除title列其余所有列属性必须为text
- 没有异步版本

## :wrench:快速上手

首先需要获得集成 Notion 的 Token 和 databbase_id 。有关如何获得Token
，请参见[查看这里](https://developers.notion.com/docs/getting-started#step-2-share-a-database-with-your-integration)
。要获取databbase_id，请查看Notion文档中的查询数据库页面的URL。

```python
from easyNotion import easyNotion

db = easyNotion(notion_id='notion_id', token='token')

# 获取全部未处理的表
table_all = db.getTableAll()

# 获取处理后的表
table = db.getTable()

# 根据指定列名col查询该列
ret = db.queryCol(col="column_name")

# 查找指定列的行
row = db.queryRow(col="column_name", content="column_content")

# 获取总行数
row_count = db.getRowCnt()

# 插入数据
data = {"title": "test_title", "column_name1": "value1", "column_name2": "value2"}
res = db.insert(data=data)

# 更新数据
res = db.update(,

# 删除数据
res = db.delete()

# 关闭session
db.closeSession()
```

类：easyNotion
-------------

### 构造函数

```python
def __init__(self, database_id, token)
```

* 初始化 `easyNotion` 类的新实例。
* 参数:
    * `database_id` (str): Notion 数据库的ID。
    * `token` (str): 用于访问 Notion API 的 API 令牌。

### 类属性

#### `baseUrl`

- 类型：字符串
- 描述：API的基础URL

#### `database_id`

- 类型：字符串
- 描述：数据库的ID

#### `headers`

- 类型：字典
- 描述：请求头信息，包括Accept、Notion-Version、Content-Type、Authorization等

#### `session`

- 类型：`requests.Session`对象
- 描述：用于发送HTTP请求的会话对象

#### `table`

- 类型：列表

- 描述：处理后的数据表，包含数据库中的所有行

### 方法

#### `getTableAll()`

```python
def getTableAll(self) -> dict
```

* 从 Notion 数据库中检索原始数据表。
* 返回:
    * 包含数据库中所有未处理数据的 JSON 对象。

#### `getTable()`

```python
def getTable(self) -> list
```

* 从 Notion 数据库中检索处理后的数据表。
* 返回:
    * 包含表示处理后数据表的字典列表。
* 注意:
    * 此方法内部调用 `getTableAll()` 来获取原始数据并对其进行处理以获得最终的数据表。

#### `queryCol(col: str) -> list`

```python
def queryCol(self, col: str) -> list
```

* 查询数据表中的特定列并返回其值。
* 参数:
    * `col` (str): 要查询的列的名称。
* 返回:
    * 包含指定列中值的字符串列表。

#### `queryRow(col: str, content: str) -> dict`

```python
def queryRow(self, col: str, content: str) -> dict
```

* 根据特定列及其内容在数据表中查询行。
* 参数:
    * `col` (str): 要搜索的列的名称。
    * `content` (str): 要在指定列中搜索的值。
* 返回:
    * 表示匹配行的原始数据的字典。
* 注意:
    * 如果未找到匹配的行，则返回一个空字典 `{}`。

#### `getRowCnt() -> int`

```python
def getRowCnt(self) -> int
```

* 检索数据表中的总行数。
* 返回:
    * 表示表中总行数的整数。

#### `insert(data: dict)`

```python
def insert(self, data: dict)
```

* 向 Notion 数据库插入数据。
* 参数:
    * `data` (dict): 要插入的数据。字典中的第一个值必须对应于 "title" 列的值。
* 返回:
    * API 请求的响应对象。

#### `update(col: str, content: str, update_col: str, update_content: str, isTitle=False)`

```python
def update(self, col: str, content: str, update_col: str, update_content: str, isTitle=False)
```

* 更新数据表中某一行的特定列。
* 参数:
    * `col` (str): 用于标识行的列。
    * `content` (str): 用于标识行的指定列的内容。
    * `update_col` (str): 要更新的列的名称。
    * `update_content` (str): 要在指定列中更新的新内容。
    * `isTitle` (bool): 表示指定列是否为标题列。默认为 `False`，若更新的列为title列，则应为True。
* 返回:
    * API 请求的响应对象。

#### `delete(col: str, content: str)`

```python
def delete(self, col: str, content: str)
```

* 根据特定列及其内容从数据表中删除一行。
* 参数:
    * `col` (str): 要删除的列的名称。
    * `content` (str): 标识删除列中行的值。
* 返回:
    * API 请求的响应对象。

#### `closeSession()`

```python
def closeSession(self)
```

* 关闭用于进行 API 请求的会话。