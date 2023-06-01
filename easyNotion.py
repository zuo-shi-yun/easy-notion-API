import json

import requests


class easyNotion:
    def __init__(self, database_id, token):
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
        self.session = requests.Session()
        # 关闭代理
        self.session.trust_env = False
        # 数据表
        self.table = self.getTable()

    # 获得原始数据表
    def getTableAll(self):
        """
        :return: 获得数据库中的全部的未处理数据,若成功返回json对象,结果按照no列递增排序,失败则返回错误代码\n
        """
        # 发送请求
        res = self.session.request("POST", self.baseUrl + 'databases/' + self.database_id + '/query',
                                   headers=self.headers)
        if res.status_code != 200:
            raise Exception('An error occurred:网络链接失败' + str(res))

        # 转为json对象
        table = json.loads(res.text)
        temp = table['results']
        # 排序
        table['results'] = sorted(temp, key=lambda x: int(x['properties']['ID']['unique_id']['number']))

        return table

    # 获得处理后的数据表
    def getTable(self):
        """
        获得处理后的数据表
        """
        base_table = self.getTableAll()  # 未处理的表
        table = []

        for row in base_table['results']:
            info = {'id': row['id']}  # 行id,这是系统的id不是显示的ID

            for col in row['properties']:
                if row['properties'][col]['type'] == 'unique_id':  # 特殊处理ID列
                    info['ID'] = row['properties'][col]['unique_id']['prefix'] + '-' + str(
                        row['properties'][col]['unique_id']['number'])
                elif row['properties'][col]['type'] == 'title':  # 特殊处理title列
                    title = row['properties'][col]['title']
                    if len(title) != 0:
                        info[col] = row['properties'][col]['title'][0]['plain_text']
                    else:
                        info[col] = ''
                else:
                    text = info[col] = row['properties'][col]['rich_text']
                    if len(text) != 0:
                        info[col] = row['properties'][col]['rich_text'][0]['plain_text']
                    else:
                        info[col] = ''

            table.append(info)

        return table

    # 根据指定的列名col查询该列
    def queryCol(self, col: str):
        """
        :param col:字符串类型的列名\n
        :return:返回字符串列表
        """

        ret = []
        for row in self.table:
            for i in row:
                if i == col:
                    ret.append(row[i])

        return ret

    # 查找指定列的行
    def queryRow(self, col: str, content: str):
        """
        查找列名为col内容为content的行的数据\n
        :param col:
        :param content:
        :return: 返回该行的原始数据
        """

        for row in self.table:
            if row[col] == content:
                return row
        else:
            return {}

    # 获取总行数
    def getRowCnt(self):
        """
        根据数据表判断总行数\n
        :return:返回总行数
        """
        return len(self.table)

    # 插入数据
    def insert(self, data):
        """
        插入数据,data参数的第一个值必须是title列对应的值\n
        :param data:所要插入的数据,{列名1:值1,列名2:值2}\n
        """
        data = list(data.items())
        payload = {
            key: {
                "type": "rich_text",
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": str(value)
                        },
                        "plain_text": str(value)
                    }
                ]
            } for key, value in data[1:]
        }

        payload[data[0][0]] = {
            "title": [
                {
                    "type": "text",
                    "text": {
                        "content": str(data[0][1])
                    }
                }
            ]
        }

        payload = {
            "parent": {
                "database_id": self.database_id
            },
            "properties": payload
        }

        res = self.session.request("POST", self.baseUrl + 'pages', headers=self.headers, json=payload)

        return res

    # 根据col更新某一行的数据
    def update(self, col: str, content: str, update_col: str, update_content: str, isTitle=False):
        """
        根据col列的content内容找到行,将行的update_col列更新为update_content,更新列的类型只能为文本\n
        :param isTitle: 是否是标题列,默认为false
        :param col:指定列\n
        :param content:指定列的内容\n
        :param update_col:更新列的列名\n
        :param update_content:更新的内容\n
        :return:成功返回成功,失败返回错误代码
        """
        id = self.queryRow(col, content)['id']

        if not isTitle:
            data = {
                "properties": {
                    update_col: {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": update_content
                                }
                            }
                        ]
                    }
                }
            }
        else:
            data = {
                "properties": {
                    update_col: {
                        "title": [
                            {
                                'text': {'content': update_content},
                                "plain_text": update_content
                            }
                        ]
                    }
                }
            }

        return self.session.request('PATCH', self.baseUrl + 'pages/' + id, headers=self.headers, json=data)

    # 根据col字段删除行
    def delete(self, col: str, content: str):
        """
        根据col列的content内容\n
        :param col:指定列的列名\n
        :param content:指定列的内容\n
        """
        id = self.queryRow(col, content)['id']

        return self.session.request("DELETE", self.baseUrl + 'blocks/' + id, headers=self.headers)

    # 关闭session
    def closeSession(self):
        """
        关闭session
        """
        self.session.close()
