# README #

### How do I get set up? ###

* Install SciPy and NumPy in your system
** On Debian-based distros (like Ubuntu), use (apt-get install python-scipy)
** On Windows, you can (I guess) install them from here: http://www.lfd.uci.edu/~gohlke/pythonlibs/#scipy
* Create a virtualenv (Python 2), and install the packages listed on requirements.txt (pip install -r requirements.txt)
* Go to the user_interface directory, and run "npm install" to install the UI dependencies
* On the main directory, run "python main.py" (under the virtualenv)
* Using a browser, go to http://localhost:5000/