# http-client-server
This repository contains the implementation of a basic HTTP client/server. 

# Installing the project

pip install -r requirements.txt #install the requirements using pip

pip freeze > requirements.txt # atualiza o file requirements com novos possíveis requirements;

# Using makefile:

Before anything, execute make install to create the virtualenv and to install the python dependencies;

After installing, run make server to run the server.

Using other terminal, run make client and check the folder: downloaded_files. The file downloaded by the client
was saved in that directory.

It is possible to change the parameter of the client, making it possible to download files different than index.html.
use: make client ABS_PATH=/simplepage.html

If you are having problems to run the server, try using another port by changing the PORT variable in the Makefile.

To uninstall: make uninstall
