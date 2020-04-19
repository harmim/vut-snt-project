# Author: Dominik Harmim <harmim6@gmail.com>

SRC_DIR := src
IN_DIR := input
OUT_DIR := output
DOC_DIR := DOC

DOC := doc.pdf
PACK := xharmi00.tar.gz


.PHONY: run
run:


.PHONY: pack
pack: $(PACK)

$(PACK): Makefile README.md $(SRC_DIR) $(IN_DIR) $(OUT_DIR)
	make clean
	cp $(DOC_DIR)/$(DOC) .
	COPYFILE_DISABLE=1 tar -czf $@ $^ $(DOC)
	rm $(DOC)


.PHONY: clean
clean:
	rm -f $(SRC_DIR)/*.pyc $(OUT_DIR)/*.txt $(DOC) $(PACK)
