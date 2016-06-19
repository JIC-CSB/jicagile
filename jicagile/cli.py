"""Command line interface."""

import sys
import os
import argparse

import colorama
from jinja2 import Environment, FileSystemLoader

import jicagile
import jicagile.config

colorama.init()


HERE = os.path.dirname(os.path.realpath(__file__))
env = Environment(loader=FileSystemLoader(os.path.join(HERE, "templates")))
list_template = env.get_template("list.jinja2")


class CLI(object):
    """Command line interface class."""

    def __init__(self, project_directory="."):
        self.project = jicagile.Project(project_directory)

    def parse_args(self, args):
        """Return parsed arguments."""
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="command")

        # The "add" command.
        add_parser = subparsers.add_parser("add", help="Add a task")
        add_parser.add_argument("title", help="Task description")
        add_parser.add_argument("storypoints", type=int, choices=[1, 3, 5, 8],
                                help="Number of story points")
        add_parser.add_argument("-c", "--current", action="store_true",
                                help="Add to current sprint")
        add_parser.add_argument("-p", "--primary-contact",
                                choices=self.project.team.lookups,
                                help="Primary contact")
        add_parser.add_argument("-e", "--theme",
                                choices=self.project.themes.lookups,
                                help="Theme of task")

        # The "edit" command.
        edit_parser = subparsers.add_parser("edit", help="Edit a task")
        edit_parser.add_argument("fpath", help="Path to task file")
        edit_parser.add_argument("-t", "--title", help="Task description")
        edit_parser.add_argument("-s", "--storypoints",
                                 type=int, help="Number of storypoints")
        edit_parser.add_argument("-p", "--primary-contact",
                                 choices=self.project.team.lookups,
                                 help="Primary contact")
        edit_parser.add_argument("-e", "--theme",
                                 choices=self.project.themes.lookups,
                                 help="Theme of task")

        # The "list" command.
        list_parser = subparsers.add_parser("list", help="List the tasks")
        list_parser.add_argument("directory",
                                 help="Path to directory with tasks")
        list_parser.add_argument("-p", "--primary-contact",
                                 help="Primary contact")

        # The "theme" command.
        theme_parser = subparsers.add_parser("theme", help="Add or remove themes")
        theme_subparsers = theme_parser.add_subparsers(dest="subcommand")
        theme_add_parser = theme_subparsers.add_parser("add", help="Add a theme")
        theme_add_parser.add_argument("name", help="Lookup name")
        theme_add_parser.add_argument("description", help="Theme description")

        return parser.parse_args(args)

    def run(self, args):
        """Run the specified command."""
        func = getattr(self, args.command)
        func(args)

    def add(self, args):
        """Add a task."""
        self.project.add_task(args.title,
                              args.storypoints,
                              args.primary_contact,
                              args.theme,
                              args.current)

    def edit(self, args):
        """Edit a task."""
        self.project.edit_task(args.fpath,
                               args.title,
                               args.storypoints,
                               args.primary_contact,
                               args.theme)

    def list(self, args):
        """List tasks."""
        directory = args.directory
        if args.directory == "todo":
            directory = self.project.current_todo_directory
        if args.directory == "done":
            directory = self.project.current_done_directory

        if directory.endswith("/"):
            directory = directory[:-1]

        tasks = jicagile.TaskCollection.from_directory(directory)
        if args.primary_contact:
            tasks = tasks.tasks_for(args.primary_contact)

        directory = os.path.basename(directory)
        print(list_template.render(tasks=tasks,
                                              directory=directory,
                                              team=self.project.team))

    def theme(self, args):
        """Add or remove a theme from the .theme.yml file."""
        fpath = os.path.join(self.project.directory, ".themes.yml")
        themes = jicagile.config.Themes()
        if os.path.isfile(fpath):
            themes = jicagile.config.Themes.from_file(fpath)
        themes.add_member(args.name, args.description)
        themes.to_file(fpath)


def main():
    cli = CLI()
    args = cli.parse_args(sys.argv[1:])
    cli.run(args)
