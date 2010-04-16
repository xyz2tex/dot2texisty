"""Test dot2texi.sty"""
import unittest

#import dot2tex.dotparsing as dotp
#from dot2tex import dotparsing
import re, os,shutil, glob,sys,time
import re


from os.path import join,basename,splitext,normpath

import logging

# intitalize logging module
log = logging.getLogger("test_graphparser")
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
# set a format which is simpler for console use
formatter = logging.Formatter('%(levelname)-8s %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
log.addHandler(console)


# Directory with test files
BASE_DIR = join(os.path.dirname(os.path.abspath(__file__)),"")
OUTPUT_DIR = normpath(join(BASE_DIR,'output/'))

def runcmd(syscmd):
    #err = os.system(syscmd)
    sres = os.popen(syscmd)
    resdata =  sres.read()
    err = sres.close()
    if err:
        log.warning('Failed to run command:\n%s',syscmd)
        log.debug('Output:\n%s',resdata)
    return err,resdata

basicdoc = r"""
\documentclass{article}
\usepackage{tikz}
\usetikzlibrary{shapes}
\usepackage{../../dot2texi}
\begin{document}
\begin{dot2tex}[file=pepepe]
digraph G {
    a -> b -> c;
}
\end{dot2tex}
\end{document}
"""

pgfbasicdoc = r"""
\documentclass{article}
\usepackage{tikz}
\usetikzlibrary{shapes}
\usepackage{../../dot2texi}
\begin{document}
\begin{dot2tex}[pgf]
digraph G {
    a -> b -> c;
}
\end{dot2tex}
\end{document}
"""

basicgraph = r"""
digraph G {
    a_1 -> b_2 -> c_3 -> a_4;
}
"""

tikzdocpreamble = r"""
\documentclass{article}
\usepackage{../../dot2texi}
\usepackage{tikz}
\usetikzlibrary{shapes}
\begin{document}
"""

docpostamble = r"""
\end{document}
"""


def create_doc(format='tikz',*args):
    if format in ['tikz','pgf']:
        s = tikzdocpreamble
    else:
        s = pstdocpreamble
    options = ",".join(args)
    s += "\n\\begin{dot2tex}[%s]\n" % options
    s += basicgraph
    s += "\\end{dot2tex}\n"
    s += docpostamble
    return s

def create_tdoc(*args):
    return create_doc('tikz',*args)

def create_pdoc(*args):
    return create_doc('pst',*args)


cmdext = r"""
system\(dot2tex\s(?P<arguments>.*?)\)\.\.\.executed
"""

# system(dot2tex --figonly --format=pgf       -o test_pgfbasic-dot2tex-fig1.tex
#test_pgfbasic-dot2tex-fig1.dot)...executed

cmdext_re = re.compile(cmdext,re.MULTILINE|re.VERBOSE|re.DOTALL)
def extract_cmd(logdata):
    """Extract dot2tex commands from log file"""
    tmp = "".join(logdata.splitlines())
    cmds = cmdext_re.findall(tmp)
    commands = []
    for cmd in cmds:
         commands.append(cmd)
    return commands


def save_and_run(texcode,filename):
    f = open(filename,'w')
    f.write(texcode)
    f.close()
    err,res = runcmd('texify -V --pdf --quiet --tex-option=--shell-escape %s' % filename)
    logdata = open(splitext(filename)[0]+'.log').read()
    cmds = extract_cmd(logdata)
    return err,cmds


class Dot2TexITestBase(unittest.TestCase):
    def setUp(self):
        import shutil
        print "Cleaning up %s" % OUTPUT_DIR


        if not os.path.exists(OUTPUT_DIR):
            os.mkdir(OUTPUT_DIR)
        else:
            shutil.rmtree(OUTPUT_DIR,True)
            if not os.path.exists(OUTPUT_DIR):
                os.mkdir(OUTPUT_DIR)
        os.chdir(OUTPUT_DIR)


class OutputFormats(Dot2TexITestBase):
    def test_pgf(self):
        err,cmds = save_and_run(create_tdoc('pgf'),'test_pgf.tex')
        self.failIf(err)
        self.failUnless(cmds[0].find('--format=pgf') >= 0 or cmds[0].find('-fpgf') >= 0)
        err,cmds = save_and_run(create_tdoc('format=pgf'),'test_pgf2.tex')
        self.failIf(err)
        self.failUnless(cmds[0].find('--format=pgf') >= 0 or cmds[0].find('-fpgf') >= 0)


    def test_tikz(self):
        err,cmds = save_and_run(create_tdoc('tikz'),'test_tikz.tex')
        self.failIf(err)
        self.failUnless(cmds[0].find('--format=tikz') >= 0 or
            cmds[0].find('-ftikz') >= 0)
        err,cmds = save_and_run(create_tdoc('format=tikz'),'test_tikz.tex')
        self.failIf(err)
        self.failUnless(cmds[0].find('--format=tikz') >= 0 or
            cmds[0].find('-ftikz') >= 0)

    def test_defaultformat(self):
        err,cmds = save_and_run(create_tdoc(),'test_defaultformat.tex')
        self.failIf(err)
        self.failUnless(cmds[0].find('--format=tikz') >= 0 or
            cmds[0].find('-ftikz') >= 0)


class TestOptions(Dot2TexITestBase):
    def test_mathmode(self):
        err,cmds = save_and_run(create_tdoc('mathmode'),'test_mathmode.tex')
        self.failIf(err)
        self.failUnless(cmds[0].find('-tmath') >= 0)
    def test_graphstyle(self):
        err,cmds = save_and_run(create_tdoc('graphstyle={xscale=2.5,transform shape}'),'test_graphstyle.tex')
        self.failIf(err)
        self.failUnless(cmds[0].find('--graphstyle') >= 0)
    def test_scale(self):
        err,cmds = save_and_run(create_tdoc('scale=.5'),'test_scale.tex')
        self.failIf(err)
        self.failUnless(cmds[0].find('--graphstyle="scale=.5,transform shape"') >= 0,cmds[0])



if __name__ == '__main__':
    unittest.main()
    #print create_doc('tikz','pgf','sdfsdfsdf')
