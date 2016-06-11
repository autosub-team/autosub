#
# Makefile
# $Log: Makefile,v $
# Revision 1.1  2005/01/20 19:25:29  hofrat
# first shot for bash intro
#
# Revision 1.1  2005/01/19 12:44:09  hofrat
# vi manual added
#
# Revision 1.1  2004/09/12 07:41:40  hofrat
# a very brief intro to vi
#
# Revision 1.1  2004/05/28 11:00:58  hofrat
# cvs intro document conforming to OT document template
#
# Revision 1.1  2004/05/27 12:50:b06  florianb
# quality plan template
#
# Revision 1.2  2004/04/25 16:11:35  matthias
# cvs log facility has been added
#


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
#	$(BIBTEX) $(PROJECTNAME) 
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
	$(RM) *.log *.blg *.ilg *.aux *.lof *.lot *.toc *.idx *.ttt \
	*.fff *.out *~ *.bbl *.acn *.glo *.ist 

strip: clean
	$(RM) *.bbl *.ind *.dvi

realclean: strip
	$(RM) *.ps

distclean: realclean
	$(RM) *.ps.gz *.ps.bz2 *.pdf

