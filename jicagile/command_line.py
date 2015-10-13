"""Agile command line tools."""

import os
import argparse

import jicagile


def add_task_cmd(args):
    """Add a task to the backlog."""
    project = jicagile.Project(".")
    project.add_task(args.title, args.storypoints, current=args.current)


def add_task_args(subparser):
    """Argument parsing for add command."""
    parser = subparser.add_parser("add", help=add_task_cmd.__doc__)
    parser.add_argument("title", help="Task description")
    parser.add_argument("storypoints", type=int, choices=(1, 3, 5, 8),
                        help="Number of story points")


def list_tasks_cmd(args):
    """List the backlog tasks."""
    project = jicagile.Project(".")
    directory = project.backlog_directory
    if args.current:
        directory = project.current_todo_directory
    fpaths = [os.path.join(directory, fn)
              for fn in os.listdir(directory)
              if fn.endswith(".yml") or fn.endswith(".yaml")]
    tasks = jicagile.TaskCollection()
    for fp in fpaths:
        tasks.append(jicagile.Task.from_file(fp))

    sort_by = "storypoints"
    if args.sort == "t":
        sort_by = "title"

    if args.current:
        print("## Current sprint [{}]\n".format(tasks.storypoints))
    else:
        print("## Backlog [{}]\n".format(tasks.storypoints))

    for pcontact in tasks.primary_contacts:
        pcontact_tasks = tasks.tasks_for(pcontact, sort_by, args.reverse)
        print("### {}' tasks [{}]\n".format(pcontact,
                                            pcontact_tasks.storypoints))
        for t in pcontact_tasks:
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
    epilog = "Version {}".format(jicagile.__version__)
    parser = argparse.ArgumentParser(prog="agl", epilog=epilog)
    parser.add_argument("-c", "--current",
                        default=False,
                        action="store_true",
                        help="Act on current sprint")

    subparser = parser.add_subparsers(dest="cmd")

    add_task_args(subparser)
    list_tasks_args(subparser)

    args = parser.parse_args()

    if args.cmd == "add":
        add_task_cmd(args)
    elif args.cmd == "list":
        list_tasks_cmd(args)
