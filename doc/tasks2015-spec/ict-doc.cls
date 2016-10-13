
\NeedsTeXFormat{LaTeX2e}
\pdfoutput=1

\LoadClass[a4paper,11pt,german,pointednumbers,headsepline]{scrartcl}

\RequirePackage[pdftex]{hyperref} % hyperlinks in the final PDF document
\RequirePackage[ngerman,english]{varioref} % references in changing styles
\RequirePackage{xspace}   % spaces after macros
\RequirePackage{calc}     % to do length calculations
\RequirePackage[pdftex]{graphicx} % graphics package
\RequirePackage[pdftex]{color}    % color package
\usepackage[T1]{fontenc}
\RequirePackage[utf8]{inputenc} % encoding of the input file
\RequirePackage{afterpage} % to handle the float pages
\usepackage[usenames,dvipsnames,svgnames,table]{xcolor}
\usepackage{amssymb}
\usepackage{titlesec}
\usepackage{float}
\usepackage{longtable}
\usepackage{multirow}
\usepackage{lmodern}
\usepackage{fancyhdr}
\usepackage[labelfont=bf,font=footnotesize]{caption} % Beschriftung von captions fett

\usepackage[english]{babel} %language 

\setkomafont{sectioning}{\bfseries} 
\setkomafont{descriptionlabel}{\bfseries} 

\definecolor{TUBlue}{HTML}{0F6799}

\renewcommand{\labelitemi}{\textcolor{TUBlue}{$\bullet$}}
\renewcommand{\labelitemii}{\textcolor{TUBlue}{$\bullet$}}

\newcommand*\@secondofsix[6]{#2}
\newcommand{\addtotitleformat}{%
  \@ifstar{\addtotitleformat@star}{\addtotitleformat@nostar}}
\newcommand\addtotitleformat@nostar[2]{%
  \PackageError{titlesec}{non starred form of \string\addtotitleformat\space not supported}{}}
\newcommand\addtotitleformat@star[2]{%
  \expandafter\expandafter\expandafter\expandafter
  \expandafter\expandafter\expandafter\def
  \expandafter\expandafter\expandafter\expandafter
  \expandafter\expandafter\expandafter\@currentsection@font
  \expandafter\expandafter\expandafter\expandafter
  \expandafter\expandafter\expandafter{%
    \expandafter\expandafter\expandafter\@secondofsix
       \csname ttlf@\expandafter\@gobble\string#1\endcsname}%
  \titleformat*{#1}{\@currentsection@font#2}%
}

\addtotitleformat*{\section}{\color{TUBlue}}
\addtotitleformat*{\subsection}{\color{TUBlue}}
\addtotitleformat*{\subsubsection}{\color{TUBlue}}

%\renewcommand{\figurename}{Abbildung}
%\renewcommand{\tablename}{Tabelle}
%\renewcommand{\contentsname}{Inhalt}
%\renewcommand{\refname}{Referenzen}

%\usepackage[acronym]{glossaries}
%\makeglossaries
%\input{glossar.tex}
%\renewcommand\glsgroupskip{}
% Title and table of contents at start of document

\AtBeginDocument{
\thispagestyle{empty}
\includegraphics[width=2.5cm]{images/logo_tu.eps} \hspace{7cm}
\includegraphics[width=5cm]{images/logo_ict.eps}

\vspace{2cm}

\begin{center}
{\Huge \textcolor{TUBlue}{\textsf \doctitle} \\
 \textcolor{TUBlue}{\textsf \docsubtitle}}
\end{center}

\vfill

\noindent
{\bf Project:} \hfill \docproject \\
{\bf Author(s):} \hfill \docauthors \\
{\bf Reviewer:} \hfill \docreviewers \\
{\bf Version:} \hfill \docversion \\
{\bf Date:} \hfill \docdate \\
\\
{\bf Copyright:} \hfill \doccopyrighta

\hfill \doccopyrightb \\

%{\bf Dokument ID:} \hfill \docid \\

\pagestyle{fancy} %eigener Seitenstil
\fancyhf{} %alle Kopf- und Fußzeilenfelder bereinigen
\fancyhead[L]{\small \docsubtitle} %Kopfzeile links gerade Seiten
\fancyhead[C]{} %zentrierte Kopfzeile
\fancyhead[R]{\small \docdate} %Kopfzeile rechts
\renewcommand{\headrulewidth}{0.4pt} %obere Trennlinie
\fancyfoot[L]{\small TU Wien, Institute of Computer Technology} 
\fancyfoot[R]{\small \thepage} %Seitennummer
\renewcommand{\footrulewidth}{0.4pt} %untere Trennlinie



\newpage
\pagenumbering{roman} % document with arabic page numbers
\phantomsection
%\addcontentsline{toc}{section}{Inhalt}
\tableofcontents
\newpage

% Set parameters
\setlength{\parskip}{1.5 ex plus 1 ex minus 0.5 ex}
\setlength{\parindent}{0 em}
\sloppy

}
\AtEndDocument{
}
