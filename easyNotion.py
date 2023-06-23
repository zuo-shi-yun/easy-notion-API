import copy
import json
import re
from typing import Dict, List

import requests


class easyNotion:
    def __init__(self, database_id: str, token: str, sort_key: List[str] = '', reverse: List[bool] = '',
                 trust_env: bool = False):
        """
        获得notion服务\n
        :param database_id: 数据库ID\n
        :param token: 集成令牌\n
        :param sort_key: 排序的列,支持根据多列排序\n
        :param reverse: 默认升序,为True时降序\n
        :param trust_env: 是否关闭代理,默认关闭\n
        """
        # 基础url
        self.baseUrl = 'https://api.notion.com/v1/'
        # 数据库ID
        self.database_id = database_id
        # 请求头
        self.headers = {
            'Accept': 'application/json',
            'Notion-Version': '2022-06-28',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token,
            'Cookie': '__cf_bm=uxsliE4EFVpT5YkTZ6ACr1jH2vu1TjkfG1gTPXYDyKg-1683367680-0-AVbHMiNx95PBmx3aRCHSTZhivPqUb/Chgy2MTqqPTAkVweNB6jjhKyixXIak85+bXiotNY0RQCRRi3XWtGQ4L4s='
        }
        self.__sort_key = sort_key
        self.__reverse = reverse if reverse else [False] * len(sort_key)
        self.__session = requests.Session()
        # 关闭代理
        self.__session.trust_env = trust_env
        # 数据表
        self.__table = []
        self.__col_name = {}

    # 获得原始相应
    def __get_original_response(self) -> requests.Response:
        payload = {'sorts': []}

        for sort_col in zip(self.__sort_key, self.__reverse):
            payload['sorts'].append(
                {'property': sort_col[0],
                 'direction': 'descending' if sort_col[1] else 'ascending'})

            # 发送请求
        res = self.__session.request("POST", self.baseUrl + 'databases/' + self.database_id + '/query', json=payload,
                                     headers=self.headers)

        if res.status_code != 200:
            raise Exception('An error occurred:网络链接失败' + str(res.text))

        return res

    # 获得原始数据表
    def get_original_table(self) -> json:
        """
        获得原始数据表\n
        :return: 获得数据库中的全部的未处理数据,若成功返回json对象,结果按照no列递增排序,失败则返回错误代码\n
        """
        res = self.__get_original_response()

        return json.loads(res.text)

    # 根据原始表获得处理后的表
    def __get_table(self, base_table: json) -> bool:
        """
        处理数据表并返回处理后的表\n
        :param base_table: 原始数据表\n
        :return: 成功返回True
        """
        table = []
        for original_row in base_table['results']:
            row = {'id': original_row['id']}  # 行id,这是系统的id不是显示的ID

            for col in original_row['properties']:
                if original_row['properties'][col]['type'] == 'unique_id':  # 处理ID列
                    row[col] = original_row['properties'][col]['unique_id']['prefix'] + '-' + str(
                        original_row['properties'][col]['unique_id']['number'])
                    self.__col_name[col] = 'ID'
                elif original_row['properties'][col]['type'] == 'title':  # 处理title列
                    title = original_row['properties'][col]['title']
                    if len(title) != 0:
                        row[col] = original_row['properties'][col]['title'][0]['plain_text']
                    else:
                        row[col] = ''
                    self.__col_name[col] = 'title'
                elif original_row['properties'][col]['type'] == 'url':  # 处理url列
                    url = original_row['properties'][col]['url']
                    if url:
                        row[col] = url
                    else:
                        row[col] = ''
                    self.__col_name[col] = 'url'
                else:  # 处理text列
                    text = row[col] = original_row['properties'][col]['rich_text']
                    if len(text) != 0:
                        row[col] = original_row['properties'][col]['rich_text'][0]['plain_text']
                    else:
                        row[col] = ''

                    self.__col_name[col] = 'text'
            table.append(row)

        self.__table = table
        return True

    # 获得处理后的数据表,避免重复查询
    def get_table(self) -> List[Dict[str, str]]:
        """
        获得处理后的数据表\n
        :return: 处理后的数据表
        """
        if self.__table:
            return copy.deepcopy(self.__table)

        base_table = self.get_original_table()  # 未处理的表
        self.__get_table(base_table)

        return copy.deepcopy(self.__table)

    # 获得列名称列表
    def get_col_name(self) -> Dict[str, str]:
        """
        获得列名称:列类型列表\n
        :return: 列名称字典,{'text':['文本类型的列名'],'ID':'ID类型的列明','title':'title类型的列名'}
        """
        if self.__col_name:
            return copy.deepcopy(self.__col_name)

        self.get_table()
        return copy.deepcopy(self.__col_name)

    # 获取总行数
    def get_row_cnt(self) -> int:
        """
        根据数据表判断总行数\n
        :return:返回总行数
        """
        return len(self.get_table())

    # 判断是否符合条件
    def __is_match_condition(self, row: Dict[str, str], condition: Dict[str, str]) -> bool:
        """
        判断row是否符合条件condition,condition为正则表达式\n
        :param row: 行Dict格式
        :param condition: 条件,Dict格式
        :return: 符合条件返回True，否则返回False
        """

        for i in condition:
            if not re.match(row[i], condition[i]):
                return False
        else:
            return True

    # 通用查询
    def query(self, query_col: List[str], query_condition: Dict[str, str] = '') -> [List[Dict[str, str]], List]:
        """
        根据query_condition条件对数据表的query_col列进行查询\n
        :param query_col:要查询的列名,为空列表时查询所有的列\n
        :param query_condition:查询条件,{'列名':'列值'},默认查询全部行\n
        :return:满足条件的行,当只查询一列时返回一个列表
        """
        table = self.get_table()
        ret = []

        # 遍历表
        for row in table:
            # 判断是否满足条件
            if self.__is_match_condition(row, query_condition):
                if query_col:  # 查询特定列时
                    if len(query_col) == 1:  # 只查询一列
                        temp_row = row[query_col[0]]
                    else:  # 查询多列
                        temp_row = {col: row[col] for col in query_col}
                else:  # 查询所有列返回整行
                    temp_row = row

                ret.append(temp_row)

        return copy.deepcopy(ret)

    # 查询一个数据
    def query_cell(self, query_condition: Dict[str, str], find_col: str) -> str:
        """
        根据key_col列的content数据查找find_col列的数据\n
        :param query_condition: 查询条件,{'列名':'列值'}\n
        :param find_col:查找列的列明\n
        :return:返回该单元格的内容
        """
        for row in self.get_table():
            if self.__is_match_condition(row, query_condition):
                return copy.deepcopy(row[find_col])
        else:
            return ''

    # 得到各种类型数据的用于更新、插入数据的payload
    def __get_payload(self, col_name: str, content: str) -> Dict[str, dict]:
        """
        得到各种类型的用于更新、插入数据的payload\n
        :param col_name:列名称\n
        :param content:要插入或更新的内容\n
        :return:一个包含用于更新、插入的payload的Dict\n
        """
        col_names = self.get_col_name()

        if col_names[col_name] == 'title':  # 标题类型
            return {
                col_name: {
                    "title": [
                        {
                            'type': 'text',
                            'text': {'content': str(content)},
                            "plain_text": str(content)
                        }
                    ]
                }
            }
        elif col_names[col_name] == 'text':  # 文本类型
            return {
                col_name: {
                    "type": "rich_text",
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": str(content)
                            },
                            "plain_text": str(content)
                        }
                    ]
                }}
        elif col_names[col_name] == 'url':  # url类型
            return {
                col_name: {
                    'type': 'url',
                    'url': str(content) if content else ' '
                }
            }
        else:
            return {}

    def insert(self, data: Dict[str, str]) -> requests.models.Response:
        """
        插入数据\n
        :param data:所要插入的数据,{列名1:值1,列名2:值2}\n
        """

        col_names = self.get_col_name()
        payload = {}

        for col_name in col_names:
            if col_name in data:
                payload.update(self.__get_payload(col_name, data[col_name]))
            else:
                payload.update(self.__get_payload(col_name, ''))

        payload = {
            "parent": {
                "database_id": self.database_id
            },
            "properties": payload
        }

        res = self.__session.request("POST", self.baseUrl + 'pages', headers=self.headers, json=payload)

        # 更新表
        self.__get_table(self.get_original_table())

        return res

    # 根据col更新某一行的数据
    def update(self, update_condition: Dict[str, str], update_data: Dict[str, str]) -> requests.models.Response:
        """
        根据col列的content内容找到行,将行的update_col列更新为update_content,更新列的类型只能为文本\n
        :param update_condition: 更新条件,{'列名':'列值'}\n
        :param update_data: 更新的数据\n
        :return:成功返回成功,失败返回错误代码
        """
        payload = {"properties": {}}
        for col_name in update_data:
            payload['properties'].update(self.__get_payload(col_name, update_data[col_name]))

        id = self.query_cell(update_condition, 'id')

        ret = self.__session.request('PATCH', self.baseUrl + 'pages/' + id, headers=self.headers, json=payload)

        # 更新表
        if ret.ok:
            table = self.get_table()
            for row in table:
                if self.__is_match_condition(row, update_condition):
                    for col_name in update_data:
                        row[col_name] = update_data[col_name]
                break

            self.__table = table

        return ret

    # 根据col字段删除行
    def delete(self, delete_condition: Dict[str, str]) -> requests.models.Response:
        """
        根据col列的content内容\n
        :param delete_condition: 删除条件,{'列名':'列值'}\n
        :return:返回响应对象
        """
        id = ''

        for row in self.get_table():
            for condition in delete_condition:
                if row[condition] == delete_condition[condition]:
                    id = row['id']
                    break

        ret = self.__session.request("DELETE", self.baseUrl + 'blocks/' + id, headers=self.headers)

        # 更新表
        if ret.ok:
            table = self.get_table()
            for row in table:
                if self.__is_match_condition(row, delete_condition):
                    table.remove(row)
                    break

            self.__table = table

        return ret

    # 关闭session
    def close_session(self) -> None:
        """
        关闭session
        """
        return self.__session.close()

    # 垃圾回收器
    def __del__(self):
        self.close_session()
