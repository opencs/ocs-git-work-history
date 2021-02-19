# OpenCS Git Work History
Copyright (c) 2021 Open Communications Security

## Description

**OpenCS Git Work History** is a small console tool written in Python 3 that
was designed to create simple report of activities on Git repositories, specially
those who use the branch-on-feature mode.

It generates a simple reports in HTML 5 that shows the number of lines of code (LOC) 
contributed and/or removed by each developer on each day of work on all
branches of the target repository.

This allows managers and customers to have at least an idea about how
much the team is working on the repository and assess the amount of 
work done. Although LOCs are known to be a crude measurement for
productivity, it can, at least, show the trends on the productivity
of the team.

This tool is inspired by other Git statistics tools such as
**gitinspector** and **gitstats** but are focused on the overall
repository statistics instead of a detailed brench details. So, if
you need this kind of report, please look for tools like 
[**gitstats**](http://gitstats.sourceforge.net/), 
[**gitinspector**](https://github.com/ejwa/gitinspector), etc.

## Features

* Scan all changes in all branches in the repository (good for repositories with multiple branches);
* Can identify and merge authors with distinct names and/or emails in the logs;
* Change summary for the whole repository;
    * Daily and weekly activity histograms with charts;
    * List of changes per file with color coding;
* Change summary for each author;
    * Daily and weekly activity histograms with charts;
    * List of changes per file with color coding;

These are the features that may be added in the future:

* Statistics based on file types;
* Identification of renames;
* List of branches in the repository;

### Limitations

* Everything is performed in memory so it may use a lot of memory if the repository is large;
* The UI is quite ugly (I'm not a designer, contributions and suggestions are welcome!);
* The navigation is clumsy if the number of charts is large (not impossible to navigate but it could be better);
* Some visualization issues with repositories with a long history;
* Some charts need to be divided in multiple images as they may contain too much information to visualize;
* Charts with no activity are still visible;
* No customization options yet;

### Demo

If you want to see how the report is generated, see this [demo](sample/index.html).

## Dependencies

This tool requires the following dependencies:

* Git 2.27.0 or later;
* Python 3.8.x or later (at least for now);
    * pygal 2.4.0 or later
    * jinja2 2.11.2 or later

The other Python dependencies are defined in the file 
**requirements.txt** and may be installed using **pip**.
It is recommended to run this program inside a virtualenv
so it will not mess with the global dependencies in the system.

### Creating the virtualevn

To create the virtualenv, just run:

```
$ python -m venv .env
```

## How to execute it

### Prepare the repository

In order to explore all information in the repository, this tool
requires a mirror clone of the repository. Do this by running:

```
$ git clone --mirror <repository address>
```

If you need to update this repository later, just run
``git remote update`` inside it to fetch all remote changes.

### Running this tool

To run this tool, just execute:

```
$ python git-work-history.py <repository location> <output directory>
```

This should generate the report file inside the output directory.

## License

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either [version 3](LICENSE.md) of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

## Contributions

This project started as a simple tool to mesure the activities of the 3rd-party
collaborators of our project, specially those that work at hourly rates. Even if
this tool is not good measure the real work performed by them, it makes it easier
to spot periods with evident low productivity or no productivity at all.

If you have the same need, feel free to use it and even help to enhance it if 
you want to.

For now, we are not ready to receive pull requests yet but you can report bugs and
suggestions on [github](https://github.com/opencs/ocs-git-work-history/issues).

## FAQ

### What do I need to run this tool?

For now, a Python 3 installation with the required dependencies. This program was
developed and tested on a Linux machine. Execution on other systems are not
supported yet (help with tests and port are welcome).

### Can I use this program for commercial purposes?

Yes, although the program itself is licensed under GPLv3, the files created by
it can be used freely.

### Can I use this program or parts of it in a commercial product?

No, any derivative work of this program must be licensed under the
GNU General Public License, Version 3 or later.
