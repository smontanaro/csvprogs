SUBDIRS = csvprogs data_filters mpl

.PHONY: all
all: FORCE
	for d in $(SUBDIRS) ; do $(MAKE) -C $$d all ; done

.PHONY: install
install: FORCE
	for d in $(SUBDIRS) ; do $(MAKE) -C $$d install ; done

.PHONY: clean
clean: FORCE
	for d in $(SUBDIRS) ; do $(MAKE) -C $$d clean ; done

.PHONY: FORCE
FORCE:
