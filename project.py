#! python

import db_wrapper

cdx_data = db_wrapper.DataWrapper()


class Project:
    pid = 0
    name = ''
    touched = 0
    pages = []
    categories = []

    def __init__(self, init_id, init_name, init_touched):
        self.pid = init_id
        self.name = init_name
        self.touched = init_touched
        self.pages = cdx_data.get_project_pages(init_id)
        self.categories = cdx_data.get_project_categories(self.pages)

    def get_pages_by_category(self):
        temp_list = self.pages
        temp_dict = {}

        for cat in self.categories:
            temp_dict[cat[1]] = []
            for page in temp_list:
                if page[4] == cat[0]:
                    temp_dict[cat[1]].append(page)
                    temp_list.remove(page)
            temp_dict[cat[1]].sort(key=lambda row: row[1])

        return temp_dict


def get_projects():
    final_list = []
    project_rows = cdx_data.get_project_list()
    project_rows.sort(key=lambda row: row[2], reverse=True)

    for r in project_rows:
        final_list.append(Project(r[0], r[1], r[2]))

    return final_list


def get_categories():
    return cdx_data.get_categories()
