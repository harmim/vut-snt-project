# Author: Dominik Harmim <harmim6@gmail.com>

SRC_DIR := src
PACK :=


.PHONY: run
run:


.PHONY: pack
pack: $(PACK)

$(PACK):


.PHONY: clean
clean:
	rm -f $(SRC_DIR)/*.pyc
