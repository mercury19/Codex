#! python

import datetime
import sqlite3


class DataWrapper:

    # TODO Add more default categories?
    default_cat = ['Main', 'Character', 'Location', 'Organization']

    def __init__(self):
        self.data = sqlite3.connect('data.db',
                                    detect_types=sqlite3.PARSE_DECLTYPES |
                                    sqlite3.PARSE_COLNAMES)
        self.data.execute("PRAGMA foreign_keys = 1")

        self.cur = self.data.cursor()

        # Create the project table if it does not exist.
        # Fields:
        # project_id: Integer; Primary Key.
        # project_title: String; Name of the project.
        # project_touched: Timestamp; Time of last modification.
        #
        # TODO add fields:
        # project_author: String; The creator/author of the project
        # project_genre: String; The genre of the project
        self.cur.execute("CREATE TABLE IF NOT EXISTS project(project_id "
                         "INTEGER PRIMARY KEY, project_title, "
                         "project_touched)")

        # Create the page table if it does not exist.
        # Fields:
        # page_id: Integer; Primary Key
        # page_title: String; Title of the page.
        # page_touched: Timestamp; Time of last modification
        # page_project: Integer; Foreign Key for the project table project_id
        # page_category: Integer; Foreign Key for the category table cat_id
        # page_text: String; The raw text of the page.
        self.cur.execute("CREATE TABLE IF NOT EXISTS page(page_id INTEGER "
                         "PRIMARY KEY, page_title, page_touched, "
                         "page_project, page_category, page_text, FOREIGN "
                         "KEY(page_project) REFERENCES project(project_id) "
                         "ON DELETE CASCADE, FOREIGN KEY(page_category) "
                         "REFERENCES category(cat_id))")

        # Create the category table if it does not exist.
        # Fields:
        # cat_id: Integer; Primary Key
        # cat_name: String; Name of the category.
        self.cur.execute("CREATE TABLE IF NOT EXISTS category(cat_id INTEGER "
                         "PRIMARY KEY, cat_name)")

        # Set default categories from list above.
        if len(self.cur.execute("SELECT * FROM category").fetchall()) <= 0:
            for d in self.default_cat:
                self.cur.execute("INSERT INTO category(cat_name) VALUES(?)",
                                 (d,))

            self.data.commit()

    def get_categories(self):
        cats = self.cur.execute("SELECT * FROM category").fetchall()
        cats.pop(0)
        cats.sort(key=lambda row: row[1])

        return cats

    def create_new_project(self, title):
        text = '[p]This is the overview page[/p]'

        new_project = self.cur.execute("INSERT INTO project VALUES(?, ?, "
                                       "?) RETURNING *", (None, title,
                                                          datetime.datetime.now())).fetchone()
        pid = self.cur.lastrowid

        cat = self.cur.execute("SELECT cat_id FROM category WHERE "
                               "cat_name='Main'").fetchone()[0]

        self.cur.execute("INSERT INTO page VALUES(?, ?, ?, ?, ?, ?)",
                         (None, 'Overview', datetime.datetime.now(), pid,
                          cat, text,))

        self.data.commit()

        return new_project

    def delete_project(self, title):
        self.cur.execute("DELETE FROM project WHERE project_title = ?",
                         (title,))

        self.data.commit()

    def get_project_list(self):
        projects = self.cur.execute("SELECT * FROM project").fetchall()

        return projects

    def add_page(self, title, project, category):
        text = '[p]This is a blank page[/p]'
        self.cur.execute("INSERT INTO page VALUES (?, ?, ?, ?, ?, ?)",
                         (None, title, datetime.datetime.now(), project,
                          category,
                          text,))

        self.data.commit()

    def add_category(self, category):
        self.cur.execute("INSERT INTO category(cat_name) VALUES(?)",
                         (category,))

        self.data.commit()

    def get_project_pages(self, project):
        pages = self.cur.execute("SELECT * FROM page WHERE page_project=?",
                                 (project,)).fetchall()

        return pages

    def get_project_categories(self, page_list):
        cat_ids = []
        categories = []

        for page in page_list:
            if page.category not in cat_ids:
                cat_ids.append(page.category)

        for c in cat_ids:
            cat = self.cur.execute("SELECT * FROM category WHERE cat_id=?",
                                   (c,)).fetchone()
            categories.append(cat)

        categories.sort(key=lambda category: category[1])

        return categories

    def touch_project(self, project_id):
        self.cur.execute("UPDATE project SET project_touched=? WHERE "
                         "project_id=?", (datetime.datetime.now(),
                                          project_id,))
        self.data.commit()

    def touch_page(self, page_id):
        project_id = self.cur.execute("UPDATE page SET page_touched=? WHERE "
                                      "page_id=? RETURNING page_project",
                                      (datetime.datetime.now(),
                                       page_id)).fetchone()[0]
        self.touch_project(project_id)

        self.data.commit()
