"""Agile command line tools."""

import os
import argparse
from operator import itemgetter

import jicagile


def add_task_cmd(args):
    """Add a task to the backlog."""
    project = jicagile.Project(".")
    project.add_task(args.title, args.storypoints)


def add_task_args(subparser):
    """Argument parsing for add command."""
    parser = subparser.add_parser("add", help=add_task_cmd.__doc__)
    parser.add_argument("title", help="Task description")
    parser.add_argument("storypoints", type=int, choices=(1, 3, 5, 8),
                        help="Number of story points")


def list_tasks_cmd(args):
    """List the backlog tasks."""
    project = jicagile.Project(".")
    fpaths = [os.path.join(project.backlog_directory, fn)
              for fn in os.listdir(project.backlog_directory)
              if fn.endswith(".yml") or fn.endswith(".yaml")]
    tasks = [jicagile.task_from_file(fp) for fp in fpaths]

    sortkey = "storypoints"
    if args.sort == "t":
        sortkey = "title"

    print("## Backlog\n")
    for t in sorted(tasks, key=itemgetter(sortkey), reverse=args.reverse):
        print("- {title} [{storypoints}]".format(**t))


def list_tasks_args(subparser):
    """Argument parsing for list command."""
    parser = subparser.add_parser("list", help=list_tasks_args.__doc__)
    parser.add_argument("-s", "--sort", choices="st",
                        default="s",
                        help="Sort order s (storypoints) t (title)")
    parser.add_argument("-r", "--reverse",
                        default=False,
                        action="store_true",
                        help="Reverse order")


def main():
    parser = argparse.ArgumentParser(prog="agl")
    subparser = parser.add_subparsers(dest="cmd")

    add_task_args(subparser)
    list_tasks_args(subparser)

    args = parser.parse_args()

    if args.cmd == "add":
        add_task_cmd(args)
    elif args.cmd == "list":
        list_tasks_cmd(args)
