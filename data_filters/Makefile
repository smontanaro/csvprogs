# Update this stuff to add/delete scripts
SCRIPTS = mvavg.py ewma.py mean.py shuffle.py spline.py take.py \
	  bars.py filter.py sigavg.py square.py roundtime.py xform.py \
	  regress.py sharpe.sh
RST_FILES = data_filters.rst

### Usage:
#
# Source files are stored in SRCDIR.  If you have hand-written ReST
# documentation files, they live in RSTDIR.  The default 'all' target
# will generate output in BINDIR and MANDIR directories.

# Little, if anything, below here should need to be changed.

BINDIR = bin
SRCDIR = src
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

$(MANDIR)/%.1 : $(RSTDIR)/%.rst
	mkdir -p $(MANDIR)
	rm -f $@
	rst2man < $< \
	| sed -e '/^\.de1 rstReportMargin/,/^\.\./d' \
	      -e '/^\.de1 INDENT/,/^\.\./d' \
	      -e '/^\.de UNINDENT/,/^\.\./d' \
	| egrep -v '^\.(UN)?INDENT' > $@
	chmod 0444 $@

$(MANDIR)/%.1 : $(SRCDIR)/%.sh
	mkdir -p $(MANDIR)
	rm -f $@
	bash $< -h 2>&1 | rst2man \
	| sed -e '/^\.de1 rstReportMargin/,/^\.\./d' \
	      -e '/^\.de1 INDENT/,/^\.\./d' \
	      -e '/^\.de UNINDENT/,/^\.\./d' \
	| egrep -v '^\.(UN)?INDENT' > $@
	chmod 0444 $@

$(MANDIR)/%.1 : $(SRCDIR)/%.py
	mkdir -p $(MANDIR)
	rm -f $@
	python $< -h 2>&1 | rst2man \
	| sed -e '/^\.de1 rstReportMargin/,/^\.\./d' \
	      -e '/^\.de1 INDENT/,/^\.\./d' \
	      -e '/^\.de UNINDENT/,/^\.\./d' \
	| egrep -v '^\.(UN)?INDENT' > $@
	chmod 0444 $@

.PHONY: clean
clean: FORCE
	rm -rf $(BINDIR)
	rm -rf $(MANDIR)

.PHONY: FORCE
FORCE:
