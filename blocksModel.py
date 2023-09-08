from typing import List, Union


# 列
class Column:
    def __init__(self, id: str, parent_id: str):
        self.id = id
        self.parent_id = parent_id
        self.text_type = 'column'


# 列列表
class ColumnList:
    def __init__(self, id: str, parent_id: str):
        self.id = id
        self.parent_id = parent_id
        self.text_type = 'column_list'


# 分割线
class Divider:
    def __init__(self, id: str, parent_id: str):
        self.id = id
        self.parent_id = parent_id
        self.text_type = 'divider'

    def __repr__(self):
        return f'分割线:{self.id}'

    @staticmethod
    def get_payload():
        return {
            'type': 'divider',
            'divider': {}
        }


# github小图类
class Mention:
    def __init__(self, id: str, url: str, parent_id: str):
        self.id = id
        self.url = url
        self.parent_id = parent_id
        self.text_type = 'bulleted_list_item'

    def __repr__(self):
        return f'github小图:{self.url}'

    def get_payload(self):
        return {'bulleted_list_item': {
            'rich_text': [{
                'annotations': {},
                # 'href': self.url,
                'mention': {'link_preview': {'url': self.url},
                            'type': 'link_preview'
                            },
                'plain_text': self.url,
                'text': {'content': ''},
                'type': 'mention'
            }]
        }}


# github大图类
class LinkPreview:
    def __init__(self, id: str, url: str, parent_id: str):
        self.id = id
        self.url = url
        self.parent_id = parent_id
        self.text_type = 'link_preview'

    def __repr__(self):
        return f'github大图:{self.url}'

    def get_payload(self):
        return {
            'link_preview': {
                'url': self.url,
            },
            # 'type': 'link_preview'
        }


# 富文本类
class RichText:
    # 初始化函数
    def __init__(self, text_type: str, id: str, parent_id: str, annotations: dict = None, href: str = '',
                 plain_text: str = ''):
        """
        初始化函数
        :param annotations: 富文本配置
        :param href: 超链接
        :param plain_text:文本内容
        :param text_type: 富文本类型
        :param id: 富文本id
        """
        self.annotations = annotations if annotations else {}
        self.href = href
        self.plain_text = plain_text if plain_text else ' '
        self.text_type = text_type
        self.id = id
        self.parent_id = parent_id

    # 输出
    def __repr__(self):
        return (self.plain_text if self.plain_text != ' ' else self.text_type) + (self.href if self.href else '')

    def get_payload(self):
        ret = {self.text_type: {
            'rich_text': [{
                'plain_text': self.plain_text,
                'text': {'content': self.plain_text},
                'annotations': self.annotations,
            }]
        }}

        if self.href:
            ret[self.text_type]['rich_text'][0]['href'] = self.href
            ret[self.text_type]['rich_text'][0]['text']['link'] = {'url': self.href}

        return ret


# 块类
class Block:
    def __init__(self, content: List[Union[Divider, Mention, LinkPreview, RichText]]):
        """
        初始化函数
        :param content: 富文本对象内容
        """
        self.content = content
        self.parent_id = content[0].parent_id if len(content) else ''

    def __repr__(self):
        return ''.join([str(i) for i in self.content])

    def get_payload(self):
        ret = {}
        for i in self.content:
            ret.update(i.get_payload())
        return ret
