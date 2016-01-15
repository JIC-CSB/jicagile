"""Agile command line tools."""

import os
import argparse

import jicagile

TEAM = jicagile.Team.from_file(".team.yml")

def add_task_cmd(args):
    """Add a task to the backlog."""
    project = jicagile.Project(".")
    project.add_task(args.title, args.storypoints,
                     primary_contact=args.primary_contact,
                     current=args.current)


def add_task_args(subparser):
    """Argument parsing for add command."""
    parser = subparser.add_parser("add", help=add_task_cmd.__doc__)
    parser.add_argument("title", help="Task description")
    parser.add_argument("storypoints", type=int, choices=(1, 3, 5, 8),
                        help="Number of story points")
    parser.add_argument("-p", "--primary_contact", choices=TEAM.lookups,
                        help="Primary contact")


def edit_task_cmd(args):
    """Edit a task (file)."""
    project = jicagile.Project(".")
    project.edit_task(args.fpath,
                      title=args.title,
                      storypoints=args.storypoints,
                      primary_contact=args.primary_contact)


def edit_task_args(subparser):
    """Argument parsing for edit command."""
    parser = subparser.add_parser("edit", help=edit_task_cmd.__doc__)
    parser.add_argument("fpath", help="Path to task file")
    parser.add_argument("-t", "--title", help="Task description")
    parser.add_argument("-s", "--storypoints", type=int, choices=(1, 3, 5, 8),
                        help="Number of story points")
    parser.add_argument("-p", "--primary_contact", choices=TEAM.lookups,
                        help="Primary contact")


def list_tasks_cmd(args):
    """List the backlog tasks."""
    project = jicagile.Project(".")
    directory = project.backlog_directory
    if args.current:
        directory = project.current_todo_directory
    elif args.directory:
        directory = args.directory
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
    elif args.directory:
        print("## {} [{}]\n".format(args.directory, tasks.storypoints))
    else:
        print("## Backlog [{}]\n".format(tasks.storypoints))

    # Logic to choose set of team members to display tasks for.
    primary_contacts = tasks.primary_contacts
    if args.primary_contact:
        primary_contacts = [args.primary_contact,]

    for pcontact in primary_contacts:
        pcontact_tasks = tasks.tasks_for(pcontact, sort_by, args.reverse)
        try:
            name = TEAM.member(pcontact).first_name
        except KeyError:
            name = pcontact
        print("### {}'s tasks [{}]\n".format(name,
                                            pcontact_tasks.storypoints))
        for t in pcontact_tasks:
            print("- {title} [{storypoints}]".format(**t))

        print("")


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
    parser.add_argument("-p", "--primary_contact", choices=TEAM.lookups,
                        default=None,
                        help="Only show tasks for primary contact")
    parser.add_argument("-d", "--directory",
                        default=None,
                        help="List tasks from specific directory")


def main():
    epilog = "Version {}".format(jicagile.__version__)
    parser = argparse.ArgumentParser(prog="agl", epilog=epilog)
    parser.add_argument("-c", "--current",
                        default=False,
                        action="store_true",
                        help="Act on current sprint")

    subparser = parser.add_subparsers(dest="cmd")

    add_task_args(subparser)
    edit_task_args(subparser)
    list_tasks_args(subparser)

    args = parser.parse_args()

    if args.cmd == "add":
        add_task_cmd(args)
    elif args.cmd == "edit":
        edit_task_cmd(args)
    elif args.cmd == "list":
        if args.current and args.directory:
            parser.error("-c and -d options are mutally exclusive")
        list_tasks_cmd(args)
