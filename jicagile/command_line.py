"""Command line tools."""

import argparse

import jicagile

def add_task():
    """Add a task to the backlog."""
    parser = argparse.ArgumentParser(add_task.__doc__)   
    parser.add_argument("title", help="Task description")
    parser.add_argument("storypoints", type=int, choices=(1, 3, 5, 8),
        help="Number of story points")
    args = parser.parse_args()
   
    project = jicagile.Project(".") 
    project.add_task(args.title, args.storypoints)
