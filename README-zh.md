# easyNotion API

![easy-notion-API](https://socialify.git.ci/zuo-shi-yun/easy-notion-API/image?description=1&language=1&logo=https%3A%2F%2Fi.postimg.cc%2Ffb52nbP0%2FNotion.png&name=1&theme=Light)

[English](README.md)|简体中文

## :muscle:功能介绍

- 相较于其他API更加简单、易上手
- 有着完善的网络请求重试机制
- 支持数据库、页面的增删改查
- 查询条件支持正则

## :bangbang:使用限制

- 只可用于notion中数据库类型为"Database - Full page"的数据库
- 数据库中除title列其余所有列属性**只能为text、ID、url**
- 对页面的操作的支持度较低
- 易上手的代价是没有复杂的机制，未在大型项目上测试

## :wrench:快速上手

首先需要获得集成 Notion 的 Token 和 数据库/页面id 。有关如何获得Token，请[查看这里](https://developers.notion.com/docs/getting-started#step-2-share-a-database-with-your-integration)。
要获取数据库/页面id，请查看Notion文档中相关教程。

```python
from pprint import pprint

from easyNotion import easyNotion

db = easyNotion(notion_id='notion_id', token='token')

# 获取全部数据表
table = db.get_table()

# 查询指定的列
col = db.query(['value'], {'key': 'query_key'})
pprint(col)

# 插入新行
res = db.insert({'key': 'insert_key', 'value': 'insert_value'})
pprint(res)

# 更新指定的行
res = db.update({'value': 'new_value'}, {'key': 'update_key'})
pprint(res)

# 删除指定的行
res = db.delete({'key': 'delete_key'})
pprint(res)
```

类：easyNotion
-------------

### 构造函数

```python
def __init__(self, 
             notion_id: str, 
             token: Union[str, List[str]], 
             sort_key: List[str] = '', 
             reverse: List[bool] = '',
             retry_time=3, 
             timeout=15, 
             get_all=True, 
             is_page: bool = False, 
             need_recursion: bool = False,
             need_download: bool = False, 
             download_path: str = '', 
             trust_env: bool = False)
```

* 初始化 `easyNotion` 类的新实例。
* 参数:
    * `notion_id (str)`: Notion 数据库的ID。
    * `token (Union[str, List[str])`: 用于访问 Notion API 的 API 令牌。若有高并发需求,建议以列表形式传入多个token。
    * `sort_key (List[str])`: 数据库配置：排序的列,支持根据多列排序。
    * `reverse (List[bool])`: 数据库配置：默认升序,为True时降序，与sort_key一一对应。
    * `retry_time (int)`: 网络请求配置:重试次数,默认3次。
    * `timeout (int)`: 网络请求配置:超时时间,默认15s。
    * `get_all (bool)`: 数据库配置：是否获取所有数据，默认获取，反之仅获取数据库前100条。
    * `is_page (bool)`: 是否为页面，默认为否。
    * `need_recursion (bool)`: 页面配置:是否需要递归获得页面的数据,默认不需要。
    * `need_download (bool)`: 页面配置:是否需要下载到本地,默认不需要。
    * `download_path (str)`: 页面配置:若有文件保存到哪个目录中。
    * `trust_env (bool)`: 网络请求配置:是否信任本地环境,默认不信任。

## 方法

### 数据库相关

#### `get_table()`

```python
def get_table(self) -> List[Dict[str, str]]
```

* 从 Notion 数据库中检索全部数据表。
* 返回:全部数据表

#### `query()`

```python
query(self, query_col: List[str], query_condition: Dict[str, Union[str, re.Pattern]] = '') 
-> List[Union[str, Dict[str, str]]]
```

* 根据条件查询内容。
* 参数：
    * `query_col: List[str]`：字符串列表，表示要查询的列名。
    * `query_condition: Dict[str, Union[str, re.Pattern]]`：查询条件，字典形式，列名与内容对应。支持正则。为空时查询指定列的全部行。

* 返回:`List[Union[str, Dict[str, str]]]`
    * 查询多列时：返回字典列表,每一个字典是一行，列名与内容对应。
    * 查询一列时：返回字符串列表，即所查询的列。

#### `insert()`

```python
def insert(self, data: Dict[str, str]) -> requests.models.Response
```

* 插入数据
* 参数:
    * `data: Dict[str, str]`：插入的数据，字典形式，列名与内容对应。若未对全部列指定内容，未指定内容的列插入内容为空。
* 返回:`requests.models.Response`
    * 网络请求响应对象。

#### `update()`

```python
def update(self, update_data: Dict[str, str], update_condition: Dict[str, Union[str, re.Pattern]]) 
-> List[requests.models.Response]
```

* 根据条件更新内容。
* 参数:
    * `update_data: Dict[str, str]` : 更新内容，字典形式，列名与内容对应。
    * `update_condition: Dict[str, Union[str, re.Pattern]]`: 更新条件，字典形式，列名与内容对应。支持正则。
* 返回:`List[requests.models.Response]`
    * 符合更新条件的每一行的网络请求响应对象列表。

#### `delete()`

```python
def delete(self, delete_condition: Dict[str, Union[str, re.Pattern]]) -> List[requests.models.Response]
```

* 根据条件删除行。
* 参数：
    * `delete_condition: Dict[str, Union[str, re.Pattern]]`：删除条件，字典形式，列名与内容对应。支持正则。

* 返回:`List[requests.models.Response]`
    * 符合删除条件的每一行的网络请求响应对象列表。

#### `append()`

```python
def append(self, append_data: Dict[str, str], append_condition: Dict[str, Union[str, re.Pattern]],divide='') -> List[requests.models.Response]
```

* 根据条件追加内容
* 参数:
    * `append_data: Dict[str, str`]: 追加内容，字典形式，列名与内容对应。
    * `append_condition: Dict[str, Union[str, re.Pattern]]`：追加条件，字典形式，列名与内容对应，支持正则。
    * `divide=''`：原内容与追加内容的分隔符，默认为空。
* 返回:`List[requests.models.Response]`
    * 符合追加条件的每一行的网络请求响应对象列表。

### 页面相关(支持度较低)

#### `get_table()`

```python
def get_table(self) -> List[Dict[str, str]]
```

* 从 Notion 数据库中检索全部数据表。
* 返回:全部数据表