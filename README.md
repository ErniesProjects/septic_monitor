# Septic Monitor

### Initial Setup (only done once!)

If you haven't already, clone this repository:

```
git clone git@github.com:ErniesProjects/septic_monitor.git
```

Create a Python virtual environment (only if you haven't already).  Note - your venv does *not* get pushed to github, it is local only.

```
cd septic_monitor                                         # we want to be in the root of the repo, where this README.md is
sudo apt update                                           # update package info
sudo apt install python3-venv python3-smbus               # install python3-smbus from package repository
python3 -m venv --system-site-packages venv               # this creates a venv directory, again - only do this once!
source venv/bin/activate                                  # activate the venv
python -m pip install pip setuptools wheel --upgrade      # upgrade some essential packages in the venv
```

Cloning the repo and creating the venv only need to be done once.  Now, every time you want to work on the project, simply cd into the repository directory (with the README.md file) and activate the venv:

```
cd septic_monitor			     # if you're not already in this directory
source venv/bin/activate
```

You'll see a `(venv)` to the left of your prompt in the terminal, to let you know the venv is active.

You can install dependencies (defined in the `setup.py` script) using pip.  Again, you only have to do this once (or if you add new dependencies).  Make sure you always do this with the venv activated!

```
python3 -m pip install -e .
```   

You can now run your `main.py` script as usual:

```
python3 septic_monitor/main.py
```


### Ongoing Development

Most of the commands in the "Initial Setup" are only required once.  From now on, if you want to work on your project, simply open a terminal, `cd` into the base of the repo, and activate the `venv`:

```
cd septic_monitor
source venv/bin/activate
```

If you add additional dependencies in `setup.py`, simply run the `python3 -m pip install -e .` command again (while in the repobase directory)


### Thonny

If you want to work on your project with Thonny, simply launch it from the menu and open main.py.  You'll have to configure Thonny to use Python from the venv you created:

`Tools -> Options -> Interpreter Tab` then select `Alternative Python 3 interpreter or virtual environment` in the drop-down menu and press `Locate another python executable`.  Use the file browser to find the `venv/bin/python3` file from the root of your repository.  You'll only need to set this up once.
