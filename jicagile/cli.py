"""Command line interface."""

import argparse
import jicagile


class CLI(object):
    """Command line interface class."""

    def __init__(self, project_directory="."):
        self.project = jicagile.Project(project_directory)

    @staticmethod
    def parse_args(args):
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
        add_parser.add_argument("-p", "--primary-contact", help="Primary contact")

        # The "edit" command.
        edit_parser = subparsers.add_parser("edit", help="Edit a task")
        edit_parser.add_argument("fpath", help="Path to task file")
        edit_parser.add_argument("-t", "--title", help="Task description")
        edit_parser.add_argument("-s", "--storypoints", type=int, help="Number of storypoints")
        edit_parser.add_argument("-p", "--primary-contact", help="Primary contact")

        return parser.parse_args(args)

    def run_command(self, command, args):
        """Run the specified command."""
        func = getattr(self, command)
        func(args)

    def add(self, args):
        """Add a task."""
        self.project.add_task(args.title,
                              args.storypoints,
                              args.primary_contact,
                              args.current)

    def edit(self, args):
        """Edit a task."""
        self.project.edit_task(args.fpath,
                               args.title,
                               args.storypoints,
                               args.primary_contact)
