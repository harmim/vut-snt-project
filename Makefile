# Author: Dominik Harmim <harmim6@gmail.com>

SRC_DIR := src
IN_DIR := input
OUT_DIR := output

DOC := doc/doc.pdf
PACK := xharmi00.tar.gz
VALIDATOR := validator/validator.jar

ARGS := umps4 0 0 30
INST := umps4
PARAMS := 2 1


.PHONY: run
run:
	python3 $(SRC_DIR)/main.py $(ARGS)


.PHONY: validate
validate:
	java -jar $(VALIDATOR) $(IN_DIR)/$(INST).txt $(PARAMS) \
		$(OUT_DIR)/$(INST).txt


.PHONY: pack
pack: $(PACK)

$(PACK): Makefile README.md requirements.txt $(DOC) $(SRC_DIR) $(IN_DIR) \
		$(OUT_DIR)
	make clean
	COPYFILE_DISABLE=1 tar -czf $@ $^


.PHONY: clean
clean:
	rm -rf $(SRC_DIR)/*.pyc $(SRC_DIR)/__pycache__/ $(PACK)
