# Arguments for server.py:
HOST=localhost
PORT=10110
BASE_DIR=./server_data

# Arguments for client:
ABS_PATH=/

# Python:
INSTALLATION_DIR=installed_files
VIRTUALENV = source $(INSTALLATION_DIR)/virt_env/Scripts/activate;
PYTHON= $(VIRTUALENV) python
PIP= $(VIRTUALENV) pip 


downloaded_files: 
	mkdir downloaded_files
	mkdir downloaded_files/log


.PHONY: clean server client install uninstall
clean: 
	rm -fr downloaded_files

server:
	$(PYTHON) src/server/server.py $(HOST) $(PORT) $(BASE_DIR)

client: downloaded_files
	$(VIRTUALENV) cd downloaded_files ; python ../src/client/client.py http://$(HOST):$(PORT)$(ABS_PATH)

install:
	mkdir $(INSTALLATION_DIR)
	virtualenv $(INSTALLATION_DIR)/virt_env
	$(PIP) install -r requirements.txt

uninstall:
	rm -fr $(INSTALLATION_DIR)

