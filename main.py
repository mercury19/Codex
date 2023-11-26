#! python

import kivy
from kivy.app import App
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.uix.treeview import TreeViewLabel

import project

kivy.require('2.2.1')

# Set minimum Window Size, kind of a hack for now
Window.minimum_width = 800
Window.minimum_height = 600
Window.size = (800, 600)


# Popup widget for user to create new project.
class NewProjectPopup(ModalView):
    project_name = StringProperty()

    def add_project(self, target):
        new_project_row = project.cdx_data.create_new_project(
            self.project_name)
        new_project = project.Project(new_project_row[0], new_project_row[
            1], new_project_row[2])
        target.add_widget(ProjectEntry(project_ref=new_project))


# The buttons to open projects on the project browser screen.
# New properties:
# project: List containing the project Name and Id in that order.
class ProjectEntry(RelativeLayout):
    project_ref = ObjectProperty()

    # Method to remove the project entry from the browser as well as the
    # project from the database.
    def remove_project(self):
        project.cdx_data.delete_project(self.project_ref.name)
        self.parent.remove_widget(self)


# Nodes for the project treeview. Should contain information to get page
# from database.
# New Properties:
# page_id: Page key for database access.
class ProjectPageListNode(TreeViewLabel):
    page_id = NumericProperty()
    page_text = StringProperty()
    pass


class ContentPane(Button):
    raw_text = StringProperty()


class NewCategoryPopup(ModalView):
    pass


# Root for the app.
# New Properties:
# prev_screen: Storage for the back button, as the "previous()" method does
# not work properly as project screens are added.
class CodexRoot(ScreenManager):
    prev_screen = StringProperty()
    last_project = project.Project(None, '', None)
    pass


class CodexApp(App):
    cdx_projects = project.get_projects()
    cdx_categories = project.get_categories()
    sm = None

    # I don't know why this is how it was done, but it works so whatever.
    def build(self):
        self.sm = CodexRoot()
        self.sm.transition = NoTransition()
        if len(self.cdx_projects) > 0:
            self.sm.last_project = self.cdx_projects[0]
        self.load_proj_list(self.sm.ids.project_list)
        return self.sm

    # Method to get a list of existing projects from the database to ensure
    # the project browser screen is populated properly. Called only once,
    # on pre_enter for the project_browser screen.
    def load_proj_list(self, target):
        for p in self.cdx_projects:
            target.add_widget(ProjectEntry(project_ref=p))

    def open_project(self, new_project):
        if self.sm.last_project == new_project:
            self.sm.current = 'project_screen'
        elif self.sm.last_project is not None:
            self.clear_project_screen()
            self.sm.last_project = new_project
            self.sm.current = 'project_screen'
        else:
            self.sm.last_project = new_project
            self.sm.current = 'project_screen'

    def clear_project_screen(self):
        nodes = []
        for n in self.sm.ids.page_tree.iterate_all_nodes():
            nodes.append(n)

        for t in nodes:
            self.sm.ids.page_tree.remove_node(t)

    def load_page_tree(self):
        if len(self.sm.ids.page_tree.root.nodes) > 0:
            return
        pages_by_cat = self.sm.last_project.get_pages_by_category()

        p1 = pages_by_cat.pop('Main')[0]
        mainpage = self.sm.ids.page_tree.add_node(
            ProjectPageListNode(text=p1[1],
                                page_id=p1[0],
                                page_text=p1[5],
                                is_open=True))
        self.sm.ids.page_tree.select_node(mainpage)

        if len(pages_by_cat.items()) > 0:
            for cat, pages in pages_by_cat.items():
                cat_node = self.sm.ids.page_tree.add_node(
                    TreeViewLabel(text=cat,
                                  font_size=24,
                                  no_selection=True,
                                  is_open=True))
                for p in pages:
                    self.sm.ids.page_tree.add_node(
                        ProjectPageListNode(text=p[1],
                                            page_id=p[0],
                                            page_text=p[5],
                                            is_open=True),
                        cat_node)

    def create_category(self, cat_name):
        project.cdx_data.add_category(cat_name)
        self.cdx_categories = project.get_categories()


LabelBase.register(name='Audiowide-Regular',
                   fn_regular='Resources/Fonts/Audiowide-Regular.ttf')

if __name__ == '__main__':
    CodexApp().run()
