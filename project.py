#! python
import datetime
import db_wrapper

from dataclasses import dataclass

cdx_data = db_wrapper.DataWrapper()


@dataclass
class Page:
    id_: int
    name_: str
    touched: datetime.datetime
    project: int
    category: int
    text_: str

    def __init__(self, data):
        self.id_ = data[0]
        self.name_ = data[1]
        self.touched = data[2]
        self.project = data[3]
        self.category = data[4]
        self.text_ = data[5]


class Project:

    def __init__(self, init_id, init_name, init_touched):
        self.id_ = init_id
        self.name_ = init_name
        self.touched = init_touched
        self.pages = []
        self.get_pages(init_id)
        self.categories = cdx_data.get_project_categories(self.pages)

    def get_pages(self, new_id):
        init_pages = cdx_data.get_project_pages(new_id)
        for item in init_pages:
            self.pages.append(Page(item))

    def get_pages_by_category(self):
        temp_list = list(self.pages)
        temp_dict = {}

        for cat in self.categories:
            temp_dict[cat[1]] = []
            for page in temp_list:
                if page.category == cat[0]:
                    temp_dict[cat[1]].append(page)
                    temp_list.remove(page)
            temp_dict[cat[1]].sort(key=lambda item: item.name_)

        return temp_dict

    def update_project(self):
        cdx_data.touch_project(self.id_)

    def create_page(self, title, category):
        cdx_data.add_page(title, self.id_, category)
        self.get_pages(self.id_)
        self.update_project()


def get_projects():
    final_list = []
    project_rows = cdx_data.get_project_list()
    project_rows.sort(key=lambda row: row[2], reverse=True)

    for r in project_rows:
        final_list.append(Project(r[0], r[1], r[2]))

    return final_list


def get_categories():
    return cdx_data.get_categories()
