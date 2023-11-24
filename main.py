#! python

import kivy
from kivy.factory import Factory
from kivy.uix.label import Label
from kivy.uix.treeview import TreeViewNode, TreeViewLabel
from kivy.uix.widget import Widget

import db_wrapper

from kivy.app import App
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager, NoTransition, Screen
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView

kivy.require('2.2.1')

# Set minimum Window Size, kind of a hack for now
Window.minimum_width = 800
Window.minimum_height = 600
Window.size = (800, 600)

db = db_wrapper.DataWrapper()


# Prompt widget for user to create new project. May attempt to make into a
# popup object?
class NewProjectPrompt(RelativeLayout):
    pass


# The buttons to open projects on the project browser screen.
# New properties:
# title_txt: The name of the project as a string, to be used as the primary
# button label and passed down for the project page title
# proj_id: The database key of the project, to be passed through for
# database access once the project screen is open
class ProjectEntry(RelativeLayout):
    title_txt = StringProperty()
    proj_id = NumericProperty()

    # Method to create and open the projects screen, as the "switch_to()"
    # method doesn't play well with the screenmanager setup.
    def open_project(self, target):
        screen_name = self.title_txt + '_screen'
        if not target.has_screen(screen_name):
            proj_screen = Factory.ProjectPage(self.title_txt, self.proj_id,
                                              name=screen_name)
            target.add_widget(proj_screen)
        target.current = screen_name

    # Method to remove the project entry from the browser as well as the
    # project from the database. Need to add a line to delete the screen as
    # well. May need to add a parameter, that's a pain.
    def remove_project(self):
        db.delete_project(self.title_txt)
        self.parent.remove_widget(self)


# Scrollview to contain the treeview for the project page navigation.
# Declared here only for access in methods if necessary.
class ProjectPageList(ScrollView):
    pass


class ProjectPageListNode(TreeViewLabel):
    page_id = NumericProperty()
    pass


class ContentPane(Widget):
    pass


class ProjectPageLayout(RelativeLayout):
    pass


# Screen class for the project screen, as it must be dynamically
# created/destroyed/modified.
# New Properties:
# project: The name of the project, for title purposes
# proj_id: The database key for the project, passed from the connected
# ProjectEntry to be used for data retrieval.
class ProjectPage(Screen):
    project = StringProperty()
    proj_id = NumericProperty()

    # Init method to allow for setting of the above properties. May not be
    # necessary?
    def __init__(self, a, b, **kwargs):
        super(ProjectPage, self).__init__(**kwargs)
        self.project = a
        self.proj_id = b


# Root for the app.
# New Properties:
# prev_screen: Storage for the back button, as the "previous()" method does
# not work properly as project screens are added.
class CodexRoot(ScreenManager):
    prev_screen = StringProperty()
    pass


class CodexApp(App):
    dbref = db
    sm = None

    # I don't know why this is how it was done, but it works so whatever.
    def build(self):
        self.sm = CodexRoot()
        self.sm.transition = NoTransition()
        return self.sm

    # Method to create a new project. Could be moved to NewProjectPrompt as
    # that is the only place it should be used.
    def add_project(self, proj_title, target):
        proj_id = self.dbref.create_new_project(proj_title)
        target.add_widget(ProjectEntry(title_txt=proj_title, proj_id=proj_id))

    # Method to get a list of existing projects from the database to ensure
    # the project browser screen is populated properly. Called only once,
    # on pre_enter for the project_browser screen.
    def load_proj_list(self, target):
        proj_list_raw = self.dbref.get_project_list()
        if len(proj_list_raw) > 0 and len(target.children) == 0:
            for p in proj_list_raw:
                target.add_widget(ProjectEntry(title_txt=p[1], proj_id=p[0]))


LabelBase.register(name='Audiowide-Regular',
                   fn_regular='Resources/Fonts/Audiowide-Regular.ttf')

if __name__ == '__main__':
    CodexApp().run()
