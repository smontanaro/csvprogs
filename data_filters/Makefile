INSTDIR = $(shell for p in `echo $$PATH | sed -e 's/:/ /g'` ; do if test `echo $$p | egrep $$HOME | wc -l` -eq 1 ; then echo $$p ; break ; fi ; done)
INSTMANDIR = $(INSTDIR)/../share/man

# Update this stuff to add/delete scripts
SCRIPTS = mvavg.py ewma.py mean.py shuffle.py spline.py take.py \
	  bars.py filter.py sigavg.py square.py roundtime.py xform.py \
	  regress.py sharpe.py hull.py
RST_FILES = data_filters.rst

### Usage:
#
# Source files are stored in SRCDIR.  If you have hand-written ReST
# documentation files, they live in RSTDIR.  The default 'all' target
# will generate output in BINDIR and MANDIR directories.

# Little, if anything, below here should need to be changed.

BINDIR = bin
SRCDIR = data_filters
MANDIR = share/man/man1
RSTDIR = share/man/rst1

BIN_SCRIPTS = $(foreach s,$(SCRIPTS),$(BINDIR)/$(basename $(s)))
SRC_SCRIPTS = $(foreach s,$(SCRIPTS),$(SRCDIR)/$(s))
MAN_FILES = $(foreach s,$(SCRIPTS),$(MANDIR)/$(basename $(s)).1) \
	$(foreach s,$(RST_FILES),$(MANDIR)/$(basename $(s)).1)

.PHONY: all
all : bin man

.PHONY: bin
bin : $(BIN_SCRIPTS)

.PHONY: man
man : $(MAN_FILES)

.PHONY: lint
lint : FORCE
	pylint $(SRC_SCRIPTS)

$(BINDIR)/% : $(SRCDIR)/%.sh
	mkdir -p $(BINDIR)
	rm -f $@
	cp $< $@
	chmod 0555 $@

$(BINDIR)/% : $(SRCDIR)/%.py
	mkdir -p $(BINDIR)
	rm -f $@
	cp $< $@
	chmod 0555 $@

$(MANDIR)/%.1 : $(SRCDIR)/%.py
	mkdir -p $(MANDIR)
	rm -f $@
	python3 $< -h 2>&1 | rst2man.py \
	| sed -e '/^\.de1 rstReportMargin/,/^\.\./d' \
	      -e '/^\.de1 INDENT/,/^\.\./d' \
	      -e '/^\.de UNINDENT/,/^\.\./d' \
	| egrep -v '^\.(UN)?INDENT' > $@
	chmod 0444 $@

.PHONY: install
install: all
	for f in $(BINDIR)/* ; do \
	    rm -f $(INSTDIR)/`basename $$f` ; \
	    cp -p $$f $(INSTDIR) ; \
	done
	mkdir -p $(INSTMANDIR)
	for d in share/man/man? ; do \
	    cp -fr $$d $(INSTMANDIR) ; \
	done

.PHONY: clean
clean: FORCE
	rm -rf $(BINDIR)
	rm -rf $(MANDIR)

.PHONY: test
test: FORCE
	for f in csvprogs/test/*.sh ; do bash $f ; done

.PHONY: FORCE
FORCE:
