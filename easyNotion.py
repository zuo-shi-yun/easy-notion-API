import copy
import json
import os.path
import random
import re
from typing import Dict, List, Union

import requests


class easyNotion:
    def __init__(self, notion_id: str, token: str, sort_key: List[str] = '', reverse: List[bool] = '',
                 need_recursion: bool = False, need_download: bool = False, download_path: str = '',
                 is_page: bool = False, trust_env: bool = False, get_all=True):
        """
        获得notion服务\n
        :param notion_id: 数据库ID\n
        :param token: 集成令牌\n
        :param sort_key: 排序的列,支持根据多列排序\n
        :param reverse: 默认升序,为True时降序\n
        :param need_recursion: 是否需要递归获得页面的数据,默认不需要\n
        :param need_download: 是否需要下载到本地,默认不需要\n
        :param download_path: 若有文件保存到哪个目录中\n
        :param is_page: 是否为页面，默认为否\n
        :param trust_env: 是否关闭代理,默认关闭\n
        :param get_all: 是否获取所有数据，默认获取\n
        """
        # 基础url
        # 数据库ID
        self.notion_id = notion_id
        # 请求头
        self.is_page = is_page
        self.__need_download = need_download
        self.download_path = download_path
        self.need_recursion = need_recursion
        self.__token = token
        # 请求头
        self.__headers = {
            'Accept': 'application/json',
            'Notion-Version': '2022-06-28',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % token,
            'Connection': 'close',
            'Cookie': '__cf_bm=uxsliE4EFVpT5YkTZ6ACr1jH2vu1TjkfG1gTPXYDyKg-1683367680-0-AVbHMiNx95PBmx3aRCHSTZhivPqUb/Chgy2MTqqPTAkVweNB6jjhKyixXIak85+bXiotNY0RQCRRi3XWtGQ4L4s='
        }
        headers_list = [
            {
                'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.0.0; SM-G955U Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (iPad; CPU OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/87.0.4280.77 Mobile/15E148 Safari/604.1'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.109 Safari/537.36 CrKey/1.54.248666'
            }, {
                'user-agent': 'Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.188 Safari/537.36 CrKey/1.54.250320'
            }, {
                'user-agent': 'Mozilla/5.0 (BB10; Touch) AppleWebKit/537.10+ (KHTML, like Gecko) Version/10.0.9.2372 Mobile Safari/537.10+'
            }, {
                'user-agent': 'Mozilla/5.0 (PlayBook; U; RIM Tablet OS 2.1.0; en-US) AppleWebKit/536.2+ (KHTML like Gecko) Version/7.2.1.0 Safari/536.2+'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; U; Android 4.3; en-us; SM-N900T Build/JSS15J) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; U; Android 4.1; en-us; GT-N7100 Build/JRO03C) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; U; Android 4.0; en-us; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 7.0; SM-G950U Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.0.0; SM-G965U Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.111 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; SM-T837A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.80 Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; U; en-us; KFAPWI Build/JDQ39) AppleWebKit/535.19 (KHTML, like Gecko) Silk/3.13 Safari/535.19 Silk-Accelerated=true'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; U; Android 4.4.2; en-us; LGMS323 Build/KOT49I.MS32310c) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/102.0.0.0 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 550) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Mobile Safari/537.36 Edge/14.14263'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 6.0.1; Moto G (4)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 10 Build/MOB31T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.0.0; Nexus 5X Build/OPR4.170623.006) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 7.1.1; Nexus 6 Build/N6F26U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.0.0; Nexus 6P Build/OPP3.170518.006) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 7 Build/MOB30X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows Phone 8.0; Trident/6.0; IEMobile/10.0; ARM; Touch; NOKIA; Lumia 520)'
            }, {
                'user-agent': 'Mozilla/5.0 (MeeGo; NokiaN9) AppleWebKit/534.13 (KHTML, like Gecko) NokiaBrowser/8.5.0 Mobile Safari/534.13'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 9; Pixel 3 Build/PQ1A.181105.017.A1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.158 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 10; Pixel 4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 11; Pixel 3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.0.0; Pixel 2 XL Build/OPD1.170816.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36'
            }, {
                'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1'
            }, {
                'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
            }, {
                'user-agent': 'Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1'
            }
        ]
        # 随即添加一个代理
        self.__headers.update(random.choice(headers_list))
        self.__baseUrl = 'https://api.notion.com/v1/'
        self.__sort_key = sort_key
        self.__reverse = reverse if reverse else [False] * len(sort_key)
        self.__session = requests.Session()
        # 关闭代理
        self.__session.trust_env = trust_env
        # 数据表
        self.__table = []
        self.__col_name = {}
        self.get_all = get_all

    # 异常包裹
    @staticmethod
    def retry_decorator(max_retries=3):
        def outer(func):
            def inner(*args, **kwargs):
                exception = None
                for i in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        exception = e
                raise exception

            return inner

        return outer

    # 获得原始数据表
    @retry_decorator
    def get_original_table(self) -> json:
        """
        获得原始数据表\n
        :return: 获得数据库中的全部的未处理数据,若成功返回json对象,结果按照no列递增排序,失败则返回错误代码\n
        """
        payload = {'sorts': []}

        # 排序请求
        for sort_col in zip(self.__sort_key, self.__reverse):
            payload['sorts'].append(
                {'property': sort_col[0],
                 'direction': 'descending' if sort_col[1] else 'ascending'})

        start_cursor = None
        original_table = {}

        while True:
            if start_cursor:
                payload["start_cursor"] = start_cursor

            # 发送请求
            if self.is_page:  # 页面类型
                res = self.__session.request("GET",
                                             self.__baseUrl + 'blocks/' + self.notion_id + '/children?page_size=100',
                                             headers=self.__headers)
            else:  # 数据库类型
                res = self.__session.request("POST", self.__baseUrl + 'databases/' + self.notion_id + '/query',
                                             json=payload, headers=self.__headers)

            if res.status_code != 200:
                raise Exception('An error occurred:网络链接失败' + str(res.text))

            data = res.json()  # 转为dict格式
            # 判断原始表是为为空，不为空则追加
            if original_table:
                original_table['results'].extend(data['results'])
            else:
                original_table = data

            if not data.get("has_more") or not self.get_all:  # 没有后续或不得到全部表则跳出循环
                break

            # 记录分页位置
            start_cursor = data["next_cursor"]

        return original_table

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

    # 根据原始表获得处理后的表
    def __get_table(self, base_table: json) -> bool:
        """
        处理数据表并返回处理后的表\n
        :param base_table: 原始数据表\n
        :return: 成功返回True
        """
        # 从原始表中获得数据
        if self.is_page:
            self.__table.extend(self.__get_page_data(base_table))
        else:
            self.__table.extend(self.__get_database_data(base_table))

        return True

    # 获得页面中的数据列表
    @retry_decorator
    def __get_page_data(self, base_table: json) -> List[Dict[str, str]]:
        table = []
        for original_row in base_table['results']:
            row = {'id': original_row['id']}

            # 需要递归获得页面数据
            if self.need_recursion:
                self.__get_recursion_data(row)

            if original_row['type'] == 'image':  # 图片类型
                url = original_row['image']['file']['url']
                session = requests.session()
                session.trust_env = self.__session.trust_env
                response = session.get(url)  # 下载文件
                row['image_source_path'] = url
                image_name = re.search(r'.*/(.*\..*)\?.*', url).group(1)  # 得到文件名
                # Check if the request was successful
                if response.ok:
                    if self.__need_download:  # 需要下载到本地时才下载到本地
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

            # 需要递归获得页面数据
            if self.need_recursion:
                self.__get_recursion_data(row)

            for col in original_row['properties']:
                if original_row['properties'][col]['type'] == 'unique_id':  # 处理ID列
                    row[col] = original_row['properties'][col]['unique_id']['prefix'] + '-' + str(  # 若没有前缀则只要数字
                        original_row['properties'][col]['unique_id']['number']) if \
                        original_row['properties'][col]['unique_id']['prefix'] else str(
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

    def __get_recursion_data(self, row: dict) -> None:
        page_svc = easyNotion(row['id'], self.__token, is_page=True, need_download=self.__need_download,
                              download_path=self.download_path)
        row['page_content'] = page_svc.get_table()
        self.__col_name[row['id']] = page_svc.get_col_name()

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

    # 通用查询
    def query(self, query_col: List[str], query_condition: Dict[str, Union[str, re.Pattern]] = '') -> list:
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

    @staticmethod
    def __is_match_condition(row: Dict[str, str], condition: Dict[str, Union[str, re.Pattern]]) -> bool:
        """
        判断row是否符合条件condition,condition为正则表达式\n
        :param row: 行Dict格式
        :param condition: 条件,Dict格式,支持正则
        :return: 符合条件返回True，否则返回False
        """

        for i in condition:
            if type(condition[i]) == re.Pattern:  # 正则表达式使用正则处理
                if not re.search(condition[i], row[i]):  # 不符合正则则返回False
                    return False
            else:  # 普通字符串做普通处理
                row[i] = '\n'.join(row[i].split('\r\n'))
                condition[i] = '\n'.join(condition[i].split('\r\n'))
                if row[i] != condition[i]:  # 不相等返回False
                    return False
        else:
            return True

    @retry_decorator
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
    @retry_decorator
    def update(self, update_data: Dict[str, Union[str, re.Pattern]],
               update_condition: Dict[str, str]) -> requests.models.Response:
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

    # 根据col字段删除行
    @retry_decorator
    def delete(self, delete_condition: Dict[str, Union[str, re.Pattern]]) -> requests.models.Response:
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
