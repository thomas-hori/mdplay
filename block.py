import re
try:
    from StringIO import StringIO
except:
    from io import StringIO

import nodes
import inline
from LinestackIter import LinestackIter

def all_same(l):
    if len(l)==0:
        return False
    elif (len(l)==1) or (l[0]==all_same(l[1:])):
        return l[0]
    else:
        return False

def _parse_block(f):
    within="root"
    minibuf=""
    depth=0
    number=0
    depths=[]
    fence=None
    fenceinfo=None

    rule_re=" ? ? ?((- ?)(- ?)(- ?)+|(_ ?)(_ ?)(_ ?)+|(\* ?)(\* ?)(\* ?)+)"
    isheadatx=lambda line:line.strip() and line.startswith("#") and (not line.lstrip("#")[:1].strip()) and ((len(line)-len(line.lstrip("#")))<=6)
    isulin=lambda line:line.strip() and (all_same(line.strip()) in tuple("=-"))
    isfence=lambda line:line.strip() and (line.lstrip()[0]==line.lstrip()[1]==line.lstrip()[2]) and (line.lstrip()[0] in "`~") and ((line.lstrip()[0]=="~") or ("`" not in line.lstrip().lstrip("`")))
    isbq=lambda line:line.strip() and line.lstrip().startswith(">") and (not line.lstrip().startswith(">!"))
    issp=lambda line:line.strip() and line.lstrip().startswith(">!")
    iscb=lambda line:len(line)>=4 and all_same(line[:4])==" "
    isul=lambda line:line.strip() and (line.lstrip()[0] in "*+-") and (line.lstrip()[1:][:1] in (""," "))

    for line in f:
        line=line.replace("\0","\xef\xbf\xbd").replace("\t","    ")
        if within=="root":
            if iscb(line):
                within="codeblock"
                f.rtpma()
                continue
            elif isheadatx(line):
                within="atxhead"
                f.rtpma()
                continue
            elif re.match(rule_re, line.rstrip()):
                within="rule"
                f.rtpma()
                continue
            elif isul(line):
                within="ul"
                f.rtpma()
                continue
            elif isfence(line):
                within="fence"
                f.rtpma()
                continue
            elif isbq(line):
                within="quote"
                f.rtpma()
                continue
            elif issp(line):
                within="spoiler"
                f.rtpma()
                continue
            elif line.strip():
                within="para"
                f.rtpma()
                continue
        elif within=="atxhead":
            if not isheadatx(line):
                yield (nodes.TitleNode(inline.parse_inline(minibuf),depth))
                minibuf=""
                depth=0
                within="root"
                f.rtpma()
                continue
            deep=0
            line=line.strip()
            while line.startswith("#"):
                deep+=1
                line=line[1:]
            if depth and deep!=depth:
                yield (nodes.TitleNode(inline.parse_inline(minibuf),depth))
                minibuf=""
            depth=deep
            if all_same(line[-depth:])=="#":
                line=line[:-depth]
            line=line.strip()
            minibuf+=line+" "
        elif within=="para":
            depth+=1
            if depth==2 and isulin(line.rstrip()):
                yield (nodes.TitleNode(inline.parse_inline(minibuf),(1 if line.strip()[0]=="=" else 2)))
                minibuf=""
                depth=0
                within="root"
                f.rtpma()
                continue
            elif not line.strip():
                yield (nodes.ParagraphNode(inline.parse_inline(minibuf)))
                minibuf=""
                depth=0
                within="root"
                f.rtpma()
                continue
            elif re.match(rule_re, line.rstrip()):
                within="rule"
                depth=0
                f.rtpma()
                continue
            if line.rstrip("\r\n").endswith("  "):
                minibuf+=line.strip()+"\n"
            else:
                minibuf+=line.strip()+" "
        elif within=="ul":
            if not line.strip():
                yield (nodes.UlliNode(parse_block(minibuf),depth))
                minibuf=""
                depth=0
                depths=[]
                within="root"
                f.rtpma()
                continue
            elif re.match(rule_re, line.rstrip()):
                yield (nodes.UlliNode(parse_block(minibuf),depth))
                minibuf=""
                depth=0
                depths=[]
                within="rule"
                f.rtpma()
                continue
            elif isul(line):
                if minibuf:
                    yield (nodes.UlliNode(parse_block(minibuf),depth))
                    minibuf=""
                deep=len(line.replace("\t"," "*4))-len(line.replace("\t"," "*4).lstrip())
                if not depths:
                    depths.append(deep)
                    depth=0
                elif deep>depths[-1]:
                    depths.append(deep)
                    depth+=1
                elif deep in depths:
                    depth=depths.index(deep)
                    depths=depths[:depth+1]
                minibuf+=line.lstrip()[1:].strip()+" "
            else:
                minibuf+=line.strip()+" "
        elif within=="rule":
            yield (nodes.RuleNode())
            within="root"
        elif within=="fence":
            if fence==None:
                fence=0
                depth=len(line)-len(line.lstrip())
                line=line.lstrip()
                fchar=line[0]
                while line[:1]==fchar:
                    fence+=1
                    line=line[1:]
                fenceinfo=line
                fence*=fchar
            elif all_same(line.strip()) and (fence in line):
                yield (nodes.CodeBlockNode(minibuf,clas=fenceinfo))
                minibuf=""
                depth=0
                fence=None
                within="root"
            else:
                for i in range(depth):
                    if line[:1]==" ":
                        line=line[1:]
                minibuf+=line.rstrip("\r\n")+"\n"
        elif within=="quote":
            if isbq(line) or (line.strip() and not iscb(line) and not isulin(line) and not isfence(line) and not isul(line) and not isheadatx(line) and not issp(line)):
                line=line.lstrip()
                if line[:1]==">":line=line[1:]
                if line[:1]==" ":line=line[1:]
                minibuf+=line.rstrip("\r\n")+"\n"
            else:
                yield (nodes.BlockQuoteNode(parse_block(minibuf)))
                minibuf=""
                within="root"
                f.rtpma()
                continue
        elif within=="spoiler":
            if issp(line) or (line.strip() and not iscb(line) and not isulin(line) and not isfence(line) and not isul(line) and not isheadatx(line) and not isbq(line)):
                line=line.lstrip()
                if line[:2]==">!":line=line[2:]
                if line[:1]==" ":line=line[1:]
                minibuf+=line.rstrip("\r\n")+"\n"
            else:
                yield (nodes.SpoilerNode(parse_block(minibuf)))
                minibuf=""
                within="root"
                f.rtpma()
                continue
    if minibuf:
        if within=="fence":
            yield (nodes.CodeBlockNode(minibuf,clas=fenceinfo))
            minibuf=""
            depth=0
            fence=None
            within="root"

def parse_block(content):
    return _parse_block(LinestackIter(StringIO(content)))

def parse_file(f):
    return _parse_block(LinestackIter(f))
