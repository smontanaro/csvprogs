INSTDIR = $(shell for p in `echo $$PATH | sed -e 's/:/ /g'` ; do if test `echo $$p | egrep $$HOME | wc -l` -eq 1 ; then echo $$p ; break ; fi ; done)
INSTMANDIR = $(INSTDIR)/../share/man

# Update this stuff to add/delete scripts
PY_SCRIPTS = \
    atr.py bars.py csv2csv.py csv2json.py csv2xls.py csvcat.py \
    csvcollapse.py csvfill.py csvmerge.py csvplot.py csvsort.py dsplit.py \
    ewma.py extractcsv.py filter.py html2csv.py hull.py interp.py \
    keltner.py mean.py mvavg.py regress.py roundtime.py sharpe.py \
    shuffle.py sigavg.py spline.py square.py take.py xform.py xls2csv.py

RST_FILES = data_filters.rst

RST2MAN = $(shell which rst2man || which rst2man.py 2>/dev/null)

### Usage:
#
# Source files are stored in SRCDIR.  If you have hand-written ReST
# documentation files, they live in RSTDIR.  The default 'all' target
# will generate output in BINDIR and MANDIR directories.

# Little, if anything, below here should need to be changed.

SCRIPTS = $(PY_SCRIPTS)

BINDIR = bin
SRCDIR = csvprogs
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

.PHONY: test
test : venv
	pytest

venv : FORCE
	if [ ! -d ./venv ] ; then \
	  python -m venv --symlinks ./venv ; \
	  python -m pip install build pytest ; \
	  python -m pip install `ls -tr dist/*.whl | tail -1` ; \
	fi

$(BINDIR)/% : $(SRCDIR)/%.py
	mkdir -p $(BINDIR)
	rm -f $@
	cp $< $@
	chmod 0555 $@

$(MANDIR)/%.1 : $(RSTDIR)/%.rst
	mkdir -p $(MANDIR)
	rm -f $@
	$(RST2MAN) < $< \
	| sed -e '/^\.de1 rstReportMargin/,/^\.\./d' \
	      -e '/^\.de1 INDENT/,/^\.\./d' \
	      -e '/^\.de UNINDENT/,/^\.\./d' \
	| egrep -v '^\.(UN)?INDENT' > $@
	chmod 0444 $@

$(MANDIR)/%.1 : $(SRCDIR)/%.py
	mkdir -p $(MANDIR)
	rm -f $@
	python $< -h 2>&1 | $(RST2MAN) \
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
	rm -f $(BIN_SCRIPTS)
	rm -f $(MAN_FILES)

.PHONY: FORCE
FORCE:
