import copy
import json
import os.path
import re
from typing import Dict, List

import requests


class easyNotion:
    def __init__(self, notion_id: str, token: str, sort_key: List[str] = '', reverse: List[bool] = '',
                 need_recursion: bool = False, download_path: str = '', is_page: bool = False, trust_env: bool = False):
        """
        获得notion服务\n
        :param notion_id: 数据库ID\n
        :param token: 集成令牌\n
        :param sort_key: 排序的列,支持根据多列排序\n
        :param reverse: 默认升序,为True时降序\n
        :param need_recursion: 是否需要递归获得页面的数据\n
        :param download_path: 若有文件保存到哪个目录中\n
        :param is_page: 是否为页面，默认为否\n
        :param trust_env: 是否关闭代理,默认关闭\n
        """
        # 基础url
        # 数据库ID
        self.notion_id = notion_id
        # 请求头
        self.is_page = is_page
        self.download_path = download_path
        self.need_re_recursion = need_recursion
        self.__token = token
        self.__headers = {
            'Accept': 'application/json',
            'Notion-Version': '2022-06-28',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token,
            'Cookie': '__cf_bm=uxsliE4EFVpT5YkTZ6ACr1jH2vu1TjkfG1gTPXYDyKg-1683367680-0-AVbHMiNx95PBmx3aRCHSTZhivPqUb/Chgy2MTqqPTAkVweNB6jjhKyixXIak85+bXiotNY0RQCRRi3XWtGQ4L4s='
        }
        self.__baseUrl = 'https://api.notion.com/v1/'
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

        # 排序请求
        for sort_col in zip(self.__sort_key, self.__reverse):
            payload['sorts'].append(
                {'property': sort_col[0],
                 'direction': 'descending' if sort_col[1] else 'ascending'})

        # 发送请求
        if self.is_page:  # 页面类型
            res = self.__session.request("GET", self.__baseUrl + 'blocks/' + self.notion_id + '/children?page_size=100',
                                         headers=self.__headers)
        else:  # 数据库类型
            res = self.__session.request("POST", self.__baseUrl + 'databases/' + self.notion_id + '/query',
                                         json=payload, headers=self.__headers)

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
        # 转为json对象
        return json.loads(res.text)

    # 根据原始表获得处理后的表
    def __get_table(self, base_table: json) -> bool:
        """
        处理数据表并返回处理后的表\n
        :param base_table: 原始数据表\n
        :return: 成功返回True
        """
        # 从原始表中获得数据
        if self.is_page:
            self.__table = self.__get_page_data(base_table)
        else:
            self.__table = self.__get_database_data(base_table)

        return True

    # 获得页面中的数据列表
    def __get_page_data(self, base_table: json) -> List[Dict[str, str]]:
        table = []
        for original_row in base_table['results']:
            row = {'id': original_row['id']}

            if self.need_re_recursion:
                page_svc = easyNotion(row['id'], self.__token, is_page=True, download_path=self.download_path)
                row['page_content'] = page_svc.get_table()
                self.__col_name[row['id']] = page_svc.get_col_name()

            if original_row['type'] == 'image':  # 图片类型
                url = original_row['image']['file']['url']
                session = requests.session()
                session.trust_env = self.__session.trust_env
                response = session.get(url)  # 下载文件
                image_name = re.search(r'.*/(.*\..*)\?.*', url).group(1)  # 得到文件名
                # Check if the request was successful
                if response.ok:
                    if not os.path.exists(self.download_path):
                        os.mkdir(self.download_path)
                    path = os.path.join(self.download_path, image_name)  # 得到下载路径
                    with open(path, "wb") as image_file:
                        image_file.write(response.content)  # 保存到本地
                    row['image_download_path'] = path
                else:
                    row['image_download_path'] = 'wrong_request'
                session.close()
                self.__col_name[image_name] = 'image'
            elif original_row['type'] == 'paragraph':  # 文本类型
                text = original_row['paragraph']['rich_text']
                if len(text) != 0:
                    row['paragraph'] = original_row['paragraph']['rich_text'][0]['plain_text']
                else:
                    row['paragraph'] = ''
                self.__col_name[row['id']] = 'paragraph'
            table.append(row)

        return table

    # 获得数据库中的数据列表
    def __get_database_data(self, base_table: json) -> List[Dict[str, str]]:
        """
        获得数据库中的所有记录\n
        :param base_table: 原始数据表\n
        :return:处理后的数据
        """
        table = []
        for original_row in base_table['results']:
            row = {'id': original_row['id']}  # 行id,这是系统的id不是显示的ID

            if self.need_re_recursion:
                page_svc = easyNotion(row['id'], self.__token, is_page=True, download_path=self.download_path)
                row['page_content'] = page_svc.get_table()
                self.__col_name[row['id']] = page_svc.get_col_name()

            for col in original_row['properties']:
                if original_row['properties'][col]['type'] == 'unique_id':  # 处理ID列
                    row[col] = original_row['properties'][col]['unique_id']['prefix'] + '-' + str(
                        original_row['properties'][col]['unique_id']['number'])
                    self.__col_name[col] = 'ID'  # 列名称:列类型
                elif original_row['properties'][col]['type'] == 'title':  # 处理title列
                    title = original_row['properties'][col]['title']
                    if len(title) != 0:
                        row[col] = original_row['properties'][col]['title'][0]['plain_text']
                    else:
                        row[col] = ''
                    self.__col_name[col] = 'title'  # 列名称:列类型
                elif original_row['properties'][col]['type'] == 'url':  # 处理url列
                    url = original_row['properties'][col]['url']
                    if url:
                        row[col] = url
                    else:
                        row[col] = ''
                    self.__col_name[col] = 'url'  # 列名称:列类型
                elif original_row['properties'][col]['type'] == 'rich_text':  # 处理text列
                    text = original_row['properties'][col]['rich_text']
                    if len(text) != 0:
                        row[col] = original_row['properties'][col]['rich_text'][0]['plain_text']
                    else:
                        row[col] = ''

                    self.__col_name[col] = 'text'  # 列名称:列类型
            table.append(row)
        return table

    # 获得处理后的数据表,避免重复查询
    def get_table(self) -> List[Dict[str, str]]:
        """
        获得处理后的数据表\n
        :return: 处理后的数据表
        """
        # 已经有表则直接返回
        if self.__table:
            return copy.deepcopy(self.__table)

        # 没有表则查询
        base_table = self.get_original_table()  # 未处理的表
        self.__get_table(base_table)

        return copy.deepcopy(self.__table)

    # 获得列名称列表
    def get_col_name(self) -> Dict[str, str]:
        """
        获得列名称:列类型列表\n
        :return: 列名称字典,{'text':['文本类型的列名'],'ID':'ID类型的列明','title':'title类型的列名'}
        """
        # 已经有列名:列类型则直接返回
        if self.__col_name:
            return copy.deepcopy(self.__col_name)
        # 没有则查询
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
    @staticmethod
    def __is_match_condition(row: Dict[str, str], condition: Dict[str, str]) -> bool:
        """
        判断row是否符合条件condition,condition为正则表达式\n
        :param row: 行Dict格式
        :param condition: 条件,Dict格式
        :return: 符合条件返回True，否则返回False
        """

        for i in condition:
            if not re.search(row[i], condition[i]):  # 不符合正则则返回False
                return False
        else:
            return True

    # 通用查询
    def query(self, query_col: List[str], query_condition: Dict[str, str] = '') -> list:
        """
        根据query_condition条件对数据表的query_col列进行查询\n
        :param query_col:要查询的列名,为空列表时查询所有的列\n
        :param query_condition:查询条件,{'列名':'列值'},默认查询全部行\n
        :return:满足条件的行(当只查询一列时返回一个列表,多列时返回字典列表),查询行数,列表中元素的类型(没有结果时为None)
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

        # 遍历全部列
        for col_name in col_names:
            if col_name in data:  # 若已指定数据则插入指定数据
                payload.update(self.__get_payload(col_name, data[col_name]))
            else:  # 没有指定则为空
                payload.update(self.__get_payload(col_name, ''))

        payload = {
            "parent": {
                "database_id": self.notion_id
            },
            "properties": payload
        }

        res = self.__session.request("POST", self.__baseUrl + 'pages', headers=self.__headers, json=payload)

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
        # 获得更新payload
        for col_name in update_data:
            payload['properties'].update(self.__get_payload(col_name, update_data[col_name]))

        id = self.query(['id'], update_condition)[0]

        ret = self.__session.request('PATCH', self.__baseUrl + 'pages/' + id, headers=self.__headers, json=payload)

        # 更新表
        if ret.ok:
            table = self.get_table()
            for row in table:  # 遍历表,找到更新的行
                if row['id'] == id:
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
            for condition in delete_condition:  # 找到指定行
                if row[condition] == delete_condition[condition]:
                    id = row['id']
                    break

        ret = self.__session.request("DELETE", self.__baseUrl + 'blocks/' + id, headers=self.__headers)

        # 更新表
        if ret.ok:
            table = self.get_table()
            for row in table:
                if row['id'] == id:
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
