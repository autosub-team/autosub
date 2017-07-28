# Makefile for generating PDF documents


RM = rm -f
PDFLATEX = $(SETVARS) pdflatex
BIBTEX = bibtex
PDF2PS = pdf2ps
GZ = gzip
BZIP2 = bzip2 -f -k

PDFFILES=$(subst .tex,.pdf,$(TEXFILES))
PSFILES=$(subst .tex,.ps,$(TEXFILES))
PSGZFILES=$(subst .tex,.ps.gz,$(TEXFILES))
PSBZ2FILES=$(subst .tex,.ps.bz2,$(TEXFILES))

all: $(PDFFILES)

ps: $(PSFILES)

html: $(HTMLFILES)

psgz: $(PSGZFILES)

psbzip2: $(PSBZIP2FILES)

%.pdf: %.tex $(DEPS)
	$(PDFLATEX) $*.tex
	makeglossaries $(PROJECTNAME)
	$(BIBTEX) $(PROJECTNAME) 
#	$(BIBTEX) weblink
	$(PDFLATEX) $*.tex
	$(PDFLATEX) $*.tex

%.ps: %.pdf $(DEPS)
	$(PDF2PS) $*.pdf $*.ps

%.gz: % $(DEPS)
	$(GZ) < $* > $*.gz

%.bz2: % $(DEPS)
	$(BZIP2) $*

bib: $(PDFFILES) $(DEPS)
	$(PDFLATEX) $(TEXFILES)
	$(BIBTEX) $(BIBFILE)
	$(PDFLATEX) $(TEXFILES)
	$(PDFLATEX) $(TEXFILES)

clean:
	$(foreach DIR,$(DIRS),$(RM) $(DIR)/*.log $(DIR)/*.blg $(DIR)/*.ilg $(DIR)/*.aux $(DIR)/*.lof $(DIR)/*.lot $(DIR)/*.toc $(DIR)/*.idx \
	$(DIR)/*.ttt $(DIR)/*.fff $(DIR)/*.out $(DIR)/*~ *.bbl $(DIR)/*.acn $(DIR)/*.glo $(DIR)/*.ist $(DIR)/*.gls $(DIR)/*.glg $(DIR)/*.alg $(DIR)/*.acr)

strip: clean
	$(foreach DIR,$(DIRS),$(RM) $(DIR)/*.bbl $(DIR)/*.ind $(DIR)/*.dvi) 

realclean: strip
	$(foreach DIR,$(DIRS),$(RM) $(DIR)/*.ps)

distclean: realclean
	$(foreach DIR,$(DIRS),$(RM) $(DIR)/*.ps.gz $(DIR)/*.ps.bz2 $(DIR)/*.pdf) 

