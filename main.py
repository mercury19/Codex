#! python

import kivy
from kivy.app import App
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.label import Label
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
# Declared here so that it can be instantiated dynamically.
class NewProjectPopup(ModalView):
    pass


# The buttons to open projects on the project browser screen.
# Properties:
# project_ref: Project instance to be passed forward as project is accessed.
class ProjectEntry(RelativeLayout):
    project_ref = ObjectProperty()
    pass


# Nodes for the project treeview. Should contain information to get page
# from database.
# Properties:
# page_: Page object for data storage/manipulation.
class ProjectPageListNode(TreeViewLabel):
    page_ = ObjectProperty()
    pass


class ContentPane(Label):
    raw_text = StringProperty()


class NewCategoryPopup(ModalView):
    pass


# Root for the app.
# Properties:
# prev_screen: Storage for the back button, as the "previous()" method does
# not work properly as project screens are added.
# current_project: Property to store the currently-relevant Project Instance.
class CodexRoot(ScreenManager):
    prev_screen = StringProperty()
    current_project = ObjectProperty()
    pass


class CodexApp(App):
    cdx_projects = project.get_projects()
    cdx_categories = project.get_categories()
    cdx_root = None

    # I don't know why this is how it was done, but it works so whatever.
    def build(self):
        self.cdx_root = CodexRoot()
        self.cdx_root.transition = NoTransition()
        if len(self.cdx_projects) > 0:
            self.cdx_root.current_project = self.cdx_projects[0]
        self.build_project_list(self.cdx_root.ids.project_list)
        return self.cdx_root

    def build_project_list(self, layout):
        for project_ in self.cdx_projects:
            layout.add_widget(ProjectEntry(project_ref=project_))

    def open_project(self, project_):
        if self.cdx_root.current_project == project_:
            self.cdx_root.current = 'project_screen'
        elif self.cdx_root.current_project is not None:
            self.clear_project_screen()
            self.cdx_root.current_project = project_
            self.cdx_root.current = 'project_screen'
        else:
            self.cdx_root.current_project = project_
            self.cdx_root.current = 'project_screen'

    def clear_project_screen(self):
        nodes = []
        for node in self.cdx_root.ids.page_tree.iterate_all_nodes():
            nodes.append(node)

        for node in nodes:
            self.cdx_root.ids.page_tree.remove_node(node)

    def load_page_tree(self):
        if len(self.cdx_root.ids.page_tree.root.nodes) > 0:
            return
        pages_by_cat = self.cdx_root.current_project.get_pages_by_category()

        p1 = pages_by_cat.pop('Main')[0]
        mainpage = self.cdx_root.ids.page_tree.add_node(
            ProjectPageListNode(text=p1.name_,
                                page_=p1,
                                is_open=True))
        self.cdx_root.ids.page_tree.select_node(mainpage)

        if len(pages_by_cat.items()) > 0:
            for cat, pages in pages_by_cat.items():
                cat_node = self.cdx_root.ids.page_tree.add_node(
                    TreeViewLabel(text=cat,
                                  font_size=24,
                                  no_selection=True,
                                  is_open=True))
                for p in pages:
                    self.cdx_root.ids.page_tree.add_node(
                        ProjectPageListNode(text=p.name_,
                                            page_=p,
                                            is_open=True),
                        cat_node)

    def add_project(self, title):
        raw_project = project.cdx_data.create_new_project(title)
        new_project = project.Project(raw_project[0], raw_project[
            1], raw_project[2])
        self.cdx_root.ids.project_list.add_widget(ProjectEntry(
            project_ref=new_project), index=len(
            self.cdx_root.ids.project_list.children))
        self.cdx_projects = project.get_projects()
        self.open_project(new_project)

    def remove_project(self, project_, layout):
        project.cdx_data.delete_project(project_)
        self.cdx_root.ids.project_list.remove_widget(layout)
        self.cdx_projects = project.get_projects()

    def create_category(self, name_):
        project.cdx_data.add_category(name_)
        self.cdx_categories = project.get_categories()


LabelBase.register(name='Audiowide-Regular',
                   fn_regular='Resources/Fonts/Audiowide-Regular.ttf')

if __name__ == '__main__':
    CodexApp().run()
