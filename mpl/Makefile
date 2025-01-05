# Update this stuff to add/delete scripts
PY_SCRIPTS = csvplot.py
RST_FILES =

INSTDIR = $(shell for p in `echo $$PATH | sed -e 's/:/ /g'` ; do if test `echo $$p | egrep $$HOME | wc -l` -eq 1 ; then echo $$p ; break ; fi ; done)

INSTMODDIR = $(shell python -c 'import sys ; print(f"{sys.prefix}/lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages")')

### Usage:
#
# Source files are stored in SRCDIR.  If you have hand-written ReST
# documentation files, they live in RSTDIR.  The default 'all' target
# will generate output in BINDIR and MANDIR directories.

# Little, if anything, below here should need to be changed.

SCRIPTS = $(PY_SCRIPTS)

BINDIR = bin
SRCDIR = src/csvplot
LIBDIR = lib
MANDIR = share/man/man1
RSTDIR = share/man/rst1

BIN_SCRIPTS = $(BINDIR)/csvplot
MODULES = $(LIBDIR)/csvplot.py
SRC_SCRIPTS = $(foreach s,$(SCRIPTS),$(SRCDIR)/$(s))
MAN_FILES = $(foreach s,$(SCRIPTS),$(MANDIR)/$(basename $(s)).1) \
	$(foreach s,$(RST_FILES),$(MANDIR)/$(basename $(s)).1)

.PHONY: all
all : bin man $(MODULES)

.PHONY: bin
bin : $(BIN_SCRIPTS)

$(MODULES) : bin
	mkdir -p $(LIBDIR)
	for m in $(MODULES) ; do \
	    cp $(SRCDIR)/`basename $$m` $$m ; \
	done

.PHONY: man
man : $(MAN_FILES)

.PHONY: lint
lint : FORCE
	pylint $(SRC_SCRIPTS)

$(BINDIR)/% : $(SRCDIR)/%.py
	mkdir -p $(BINDIR)
	rm -f $@
	sed -e 's/@@VERSION@@/$(VERSION)/g' $< > $@
	chmod 0555 $@

$(MANDIR)/%.1 : $(RSTDIR)/%.rst
	mkdir -p $(MANDIR)
	rm -f $@
	rst2man.py < $< \
	| sed -e '/^\.de1 rstReportMargin/,/^\.\./d' \
	      -e '/^\.de1 INDENT/,/^\.\./d' \
	      -e '/^\.de UNINDENT/,/^\.\./d' \
	| egrep -v '^\.(UN)?INDENT' > $@
	chmod 0444 $@

$(MANDIR)/%.1 : $(SRCDIR)/%.py
	mkdir -p $(MANDIR)
	rm -f $@
	python $< -h 2>&1 | sed -e 's/@@VERSION@@/$(VERSION)/g' | rst2man.py > $@
	chmod 0444 $@

.PHONY: install
install: install-modules install-scripts

.PHONY: install-scripts
install-scripts: bin
	for f in $(BINDIR)/* ; do \
	    name=`basename $$f .py` ; \
	    scr=$(INSTDIR)/$$name ; \
	    rm -f $$scr ; \
	    echo '#!/usr/bin/env python3' > $$scr ; \
	    echo "import sys, $$name" >> $$scr ; \
	    echo "sys.exit($$name.main())" >> $$scr ; \
	    chmod +x $$scr ; \
	done

.PHONY: install-modules
install-modules: $(MODULES)
	for f in $(LIBDIR)/* ; do \
	    cp $$f $(INSTMODDIR) ; \
	    chmod 0644 $(INSTMODDIR)/`basename $$f` ; \
	done

.PHONY: clean
clean: FORCE
	rm -f $(BIN_SCRIPTS)
	rm -f $(MAN_FILES)

.PHONY: FORCE
FORCE:
