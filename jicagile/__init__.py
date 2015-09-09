"""jicagile package."""

import os
import os.path

import yaml
from slugify import slugify

__version__ = "0.0.1"


class Project(object):
    """Agile project management class."""

    def __init__(self, directory):
        self.directory = directory
        self.backlog_directory = os.path.join(directory, "backlog")
        if not os.path.isdir(self.backlog_directory):
            os.mkdir(self.backlog_directory)

    def __eq__(self, other):
        return self.directory == other.directory

    def add_task(self, title, storypoints):
        """Add a task to the backlog."""
        task = dict(title=title, storypoints=storypoints)
        fname = "{}.yml".format(slugify(title))
        fpath = os.path.join(self.backlog_directory, fname)
        with open(fpath, "w") as fh:
            yaml.dump(task, fh)
        return task


def task_from_file(fpath):
    """Return task dictionary from a task.yml file."""
    return yaml.load(file(fpath))
