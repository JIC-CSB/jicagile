========
jicagile
========

- GitHub: https://github.com/JIC-CSB/jicagile
- PyPI: https://pypi.python.org/pypi/jicagile
- Free software: MIT License

Installation
------------

To install the jicagile package.

.. code-block:: bash

    pip install jicagile

Or install it from source.

.. code-block:: bash

    git clone https://github.com/JIC-CSB/jicagile.git
    cd jicagile
    python setup.py install


Usage
-----

The package comes with a command line utility named ``agl``.
When you run the ``agl`` command it assumes that you are in
a directory where you want to store your agile project management
files.

The ``agl`` tool comes with built-in Git integration. To enable
this simply initialise the project directory as a git repository.

.. code-block:: bash

    git init

The step above is optional, but highly recommended. Git is great.

Now let's illustrate how to add a task to our agile project.
The command below creates a task with the title
``"Learn how to use agl cmd line"`` of size 3. The available
story point sizes are 1, 3, 5 and 8.

.. code-block:: bash

    agl add "Learn how to use agl cmd line" 3

This will create a ``backlog`` directory and place a file named
``learn-how-to-use-agl-cmd-line.yml`` file in it. It will also
create the directories ``current/{todo,done}``.

To move the task to the current sprint.

.. code-block:: bash

    agl mv backlog/learn-how-to-use-agl-cmd-line.yml current/todo

To mark the task as done.

.. code-block:: bash

    agl mv current/todo/learn-how-to-use-agl-cmd-line.yml current/done

To add a task to the current "todo" list one can use the ``-c`` argument
(mnemonic current).

.. code-block:: bash

    agl add -c "Email friends about jicagile" 1

To list the content of the backlog.

.. code-block:: bash

    agl list backlog/

The ``todo`` and ``done`` directories have aliases so you do not need to
specify the full path to list their content.

.. code-block:: bash

    agl list todo
    agl list done

You can edit tasks using your favorite text editor or you can use the
``agl edit`` command. For example the command below increases the number
of story points from one to five.

.. code-block:: bash

    agl edit current/todo/email-friends-about-jicagile.yml --storypoints=5

You can add themes to your project.

.. code-block:: bash

    agl theme add admin "Emails, forms, meetings, etc"
    agl edit current/todo/email-friends-about-jicagile.yml --theme=admin

Themes are stored in a ``.themes.yml`` file.

It is also possible to add team members to your project.

.. code-block:: bash

    agl teammember add TO Tjelvar Olsson
    agl teammember add MH Matthew Hartley

Team members  are stored in a ``.team.yml`` file.

You can then associate a task with a primary contact.

.. code-block:: bash

    agl add "Write report" 8 -p MH -e admin

In the above ``-p`` is the short hand for ``--primary-contact`` and
``-e`` is short hand for ``--theme``.

Note that the ``agl`` tool simply creates text files. It can be therefore be
used together with ``git``. In fact all of the commands above automatically
have Git integration built-in. It can be very satisfying to have the agile
project management files under version control on GitHub.

Once you have had your sprint review meeting and all the relevant
files have been moved to the ``current/done`` directory create a
directory named ``past_sprints``.

.. code-block:: bash

    mkdir past_sprints

Then move and rename the ``current/done`` directory there with
todays date using a year-month-day scheme.

.. code-block:: bash

    agl mv current/todo past_sprints/2016-06-19


Release notes
-------------

0.4.0
~~~~~

- *Added Git integration*
- Added ``agl mv`` command
- Fixed defect where adding to an empty config file caused and iteration error

0.3.0
~~~~~

- Added ability to add and remove team members from the command line
- Updated the format of the output from the ``agl list`` command

0.2.0
~~~~~

- Refactored and redesigned the command line interface
- Improved test coverage
- Added color to list output
- Added ability to associate a task with a theme
