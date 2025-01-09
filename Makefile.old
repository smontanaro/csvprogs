SUBDIRS = csvprogs

.PHONY: all
all: FORCE
	for d in $(SUBDIRS) ; do $(MAKE) -C $$d all ; done

.PHONY: man
man: FORCE
	for d in $(SUBDIRS) ; do $(MAKE) -C $$d man ; done

.PHONY: install
install: FORCE
	for d in $(SUBDIRS) ; do $(MAKE) -C $$d install ; done

.PHONY: clean
clean: FORCE
	for d in $(SUBDIRS) ; do $(MAKE) -C $$d clean ; done

.PHONY: lint
lint: FORCE
	for d in $(SUBDIRS) ; do $(MAKE) -C $$d lint ; done

.PHONY: FORCE
FORCE:
