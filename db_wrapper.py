#! python

import sqlite3


class DataWrapper:
    default_cat = ['Main', 'Character', 'Location', 'Organization']

    def __init__(self):
        self.data = sqlite3.connect('data.db')
        self.data.execute("PRAGMA foreign_keys = 1")

        self.cur = self.data.cursor()

        self.cur.execute("CREATE TABLE IF NOT EXISTS project(project_id "
                         "INTEGER PRIMARY KEY, project_title)")

        self.cur.execute("CREATE TABLE IF NOT EXISTS page(page_id INTEGER "
                         "PRIMARY KEY, page_title, page_touched, "
                         "page_project, page_category, page_text, page_len "
                         "INT, FOREIGN KEY(page_project) REFERENCES project("
                         "project_id) ON DELETE CASCADE, FOREIGN KEY("
                         "page_category) REFERENCES category(cat_id))")

        self.cur.execute("CREATE TABLE IF NOT EXISTS text(text_id INTEGER "
                         "PRIMARY KEY, text_page, text_content, text_flags, "
                         "FOREIGN KEY(text_page) REFERENCES page(page_id) ON "
                         "DELETE CASCADE)")

        self.cur.execute("CREATE TABLE IF NOT EXISTS category(cat_id INTEGER "
                         "PRIMARY KEY, cat_name)")

        if len(self.cur.execute("SELECT * FROM category").fetchall()) <= 0:
            for d in self.default_cat:
                self.cur.execute("INSERT INTO category(cat_name) VALUES(?)",
                                 (d,))

            self.data.commit()

    def create_new_project(self, title):
        self.cur.execute("INSERT INTO project(project_title) VALUES(?)",
                         (title,))
        pid = self.cur.lastrowid

        cat = self.cur.execute("SELECT cat_id FROM category WHERE "
                               "cat_name='Main'").fetchone()[0]

        main_page = self.cur.execute("INSERT INTO page(page_title, "
                                     "page_project, page_category) VALUES(?, "
                                     "?, ?) RETURNING page_id", ('Overview',
                                                                 pid, cat,
                                                                 )).fetchone()[
            0]

        self.cur.execute("INSERT INTO text(text_page, text_content) VALUES("
                         "?, ?)", (main_page, '[p]This is the overview page['
                                              '/p]'))

        self.data.commit()

        return pid

    def delete_project(self, title):
        self.cur.execute("DELETE FROM project WHERE project_title = ?",
                         (title,))

        self.data.commit()

    def get_project_list(self):
        res = self.cur.execute("SELECT * FROM project")
        projects = res.fetchall()

        return projects

    def get_project_pages(self, proj):
        final = {}
        catsf = []
        pages = self.cur.execute("SELECT * FROM page WHERE page_project = "
                                 "?", (proj, )).fetchall()

        cats = self.cur.execute("SELECT page_category FROM page "
                                "WHERE page_project = ?", (proj, )).fetchall()
        for c in cats:
            catsf.append(self.cur.execute("SELECT * FROM category WHERE "
                                          "cat_id = ?", (c[0], )).fetchone())

        for c in catsf:
            final[c[1]] = []
            for p in pages:
                if p[4] == c[0]:
                    final[c[1]].append(p)

        return final
