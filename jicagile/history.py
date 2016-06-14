"""Write out csv format of historical data."""

import argparse
import os
import os.path

import jicagile


def yield_date_and_subdir(parent_dir):
    for subdir in sorted(os.listdir(parent_dir)):
        path = os.path.join(parent_dir, subdir)
        if os.path.isdir(path):
            yield subdir, path


def task_collection_from_directory(directory):
    """Return a TaskCollection from a directory."""
    task_collection = jicagile.TaskCollection()
    fpaths = [os.path.join(directory, fn)
              for fn in os.listdir(directory)
              if fn.endswith(".yml") or fn.endswith(".yaml")]
    for fp in fpaths:
        task_collection.append(jicagile.Task.from_file(fp))
    return task_collection


def yield_historical_data(directory):
    """Yield historical data as csv strings."""
    for date, subdir in yield_date_and_subdir(directory):
        tasks = task_collection_from_directory(subdir)
        yield "{},{:d}".format(date, tasks.storypoints)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("past_sprints_directory")
    args = parser.parse_args()
    if not os.path.isdir(args.past_sprints_directory):
        parser.error("Not a directory: {}".format(args.past_sprints_directory))

    for csv_string in yield_historical_data(args.past_sprints_directory):
        print(csv_string)


if __name__ == "__main__":
    main()
