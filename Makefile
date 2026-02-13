.PHONY: run run-email run-code run-analysis test

run:
	python3 faang_agent.py --interactive

run-email:
	python3 faang_agent.py --mode email --interactive

run-code:
	python3 faang_agent.py --mode code --interactive

run-analysis:
	python3 faang_agent.py --mode analysis --interactive

test:
	python3 -m unittest -v
