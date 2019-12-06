
all:
	@$(MAKE) flake8
	@$(MAKE) pytest
        

pytest:
	@export PYTHONPATH=`pwd`
	@pytest

flake8:
	@flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	@flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics


default:
	@echo "Hello"
