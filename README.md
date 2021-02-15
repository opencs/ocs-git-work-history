# OpenCS Git Work History
Copyright (c) 2021 Open Communications Security

## Description

**OpenCS Git Work History** is a small tool written in Python 3 that was
designed to create simple report of ativities on Git repositories, specially
those who use the brench-on-feature mode.

It generates a simple report that shows the number of lines of code (LOC) 
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
you need this kind of report, please 

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

This software is licensed under GPLv3.


