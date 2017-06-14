import re
from xml.dom import minidom

__copying__ = """
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from mdplay import nodes, mdputil

def html_out_part(nodem,document,in_list=(),flags=()):
    return list(_html_out_part(nodem,document,in_list,flags=flags))

def _html_out_part(nodem,document,in_list=(),flags=()):
    while nodem:
        node=nodem.pop(0)
        if isinstance(node,nodes.UlliNode):
            if (node.depth+1)>len(in_list):
                r=document.createElement("ul")
                r2=document.createElement("li")
                r.appendChild(r2)
                for domn in html_out_part(node.content,document,flags=flags):
                    r2.appendChild(domn)
                for domn in html_out_part(nodem,document,("ul",)+in_list):
                    if domn.tagName not in ("ul","ol"):
                        r.appendChild(domn)
                    elif not len(r2.childNodes):
                        r3=document.createElement("li")
                        r.appendChild(r3)
                        r3.appendChild(domn)
                    else:
                        r.lastChild.appendChild(domn)
                yield r
            elif ((node.depth+1)<len(in_list)) or (in_list[0]=="ol"):
                nodem.insert(0,node)
                return
            else:
                r=document.createElement("li")
                for domn in html_out_part(node.content,document,flags=flags):
                    r.appendChild(domn)
                yield r
        elif isinstance(node,nodes.OlliNode):
            if (node.depth+1)>len(in_list):
                r=document.createElement("ol")
                r2=document.createElement("li")
                if ("autonumberonly" not in flags):
                    r2.setAttribute("value",str(node.bullet))
                r.appendChild(r2)
                for domn in html_out_part(node.content,document,flags=flags):
                    r2.appendChild(domn)
                for domn in html_out_part(nodem,document,("ol",)+in_list):
                    if domn.tagName not in ("ul","ol"):
                        r.appendChild(domn)
                    elif not len(r2.childNodes):
                        r3=document.createElement("li")
                        r.appendChild(r3)
                        r3.appendChild(domn)
                    else:
                        r.lastChild.appendChild(domn)
                yield r
            elif ((node.depth+1)<len(in_list)) or (in_list[0]=="ul"):
                nodem.insert(0,node)
                return
            else:
                r=document.createElement("li")
                if ("autonumberonly" not in flags):
                    r.setAttribute("value",str(node.bullet))
                for domn in html_out_part(node.content,document,flags=flags):
                    r.appendChild(domn)
                yield r
        elif in_list: #A non-list node at list-stack level
            nodem.insert(0,node)
            return
        elif not isinstance(node,nodes.Node): #i.e. is a string
            yield document.createTextNode(node.decode("utf-8").replace(u"\x20\x20",u"\xa0\x20"))
        elif isinstance(node,nodes.EmojiNode):
            if ("notwemoji" not in flags) and node.emphatic:
                if node.content.decode("utf-8") == u"\U000FDECD":
                    r=document.createElement("img")
                    r.setAttribute("src","http://i.imgur.com/SfHfed9.png")
                    r.setAttribute("alt",":demonicduck:")
                    yield r
                else:
                    hexcode=node.label[2]
                    altcode=node.content.decode("utf-8")
                    r=document.createElement("img")
                    r.setAttribute("src","https://twemoji.maxcdn.com/2/72x72/%s.png"%hexcode)
                    r.setAttribute("alt",altcode)
                    r.setAttribute("style","max-width:2em;max-height:2em;")
                    # Acceptable attribution per https://github.com/twitter/twemoji/blob/b33c30e78db45be787410567ad6f4c7b56c137a0/README.md#attribution-requirements
                    yield document.createComment(" twemoji, by Twitter, Inc.  Licensed under CC-BY 4.0 (http://creativecommons.org/licenses/by/4.0/), available from https://github.com/twitter/twemoji/ ")
                    yield r
            else:
                yield document.createTextNode(node.content.decode("utf-8"))
        elif isinstance(node,nodes.TitleNode):
            if node.depth>6: node.depth=6
            r=document.createElement("h%d"%node.depth)
            for domn in html_out_part(node.content,document,flags=flags):
                r.appendChild(domn)
            yield r
        elif isinstance(node,nodes.ParagraphNode):
            r=document.createElement("p")
            for domn in html_out_part(node.content,document,flags=flags):
                r.appendChild(domn)
            yield r
        elif isinstance(node,nodes.BlockQuoteNode):
            r=document.createElement("blockquote")
            for domn in html_out_part(node.content,document,flags=flags):
                r.appendChild(domn)
            yield r
        elif isinstance(node,nodes.SpoilerNode):
            if "ipsspoilers" in flags:
                metar=document.createElement("blockquote")
                metar.setAttribute("class",'ipsStyle_spoiler')
                metar.setAttribute("data-ipsspoiler",'')
                metar.setAttribute("tabindex",'0')
                r=document.createElement("div")
                metar.appendChild(r)
                r.setAttribute("class",'ipsSpoiler_header')
                r2=document.createElement("span")
                r.appendChild(r2)
                # TODO: does this actually change the title or does IPBoard override it?
                if not node.label:
                    r2.appendChild(document.createTextNode("Spoiler"))
                else:
                    for domn in html_out_part(node.label,document,flags=flags):
                        r2.appendChild(domn)
                r3=document.createElement("div")
                metar.appendChild(r3)
                r3.setAttribute("class",'ipsSpoiler_contents')
                for domn in html_out_part(node.content,document,flags=flags):
                    r3.appendChild(domn)
                yield metar
            else:
                metar=document.createElement("div")
                metar.setAttribute("class",'spoilerwrapper')
                r=document.createElement("p")
                metar.appendChild(r)
                r2=document.createElement("a")
                r.appendChild(r2)
                r2.setAttribute("href",'javascript:void(0);')
                r2.setAttribute("onclick","document.getElementById('spoil%d').style.display=(document.getElementById('spoil%d').style.display=='none')?('block'):('none')"%(mdputil.newid(node),mdputil.newid(node)))
                if not node.label:
                    r2.appendChild(document.createTextNode("Expand/Hide Spoiler"))
                else:
                    for domn in html_out_part(node.label,document,flags=flags):
                        r2.appendChild(domn)
                r3=document.createElement("div")
                metar.appendChild(r3)
                r3.setAttribute("class",'spoiler')
                r3.setAttribute("id",'spoil%d'%mdputil.newid(node))
                r3.setAttribute("style",'display:none;')
                for domn in html_out_part(node.content,document,flags=flags):
                    r3.appendChild(domn)
                yield metar
        elif isinstance(node,nodes.CodeBlockNode):
            r=document.createElement("pre")
            r.appendChild(document.createTextNode("".join(node.content).decode("utf-8")))
            yield r
        elif isinstance(node,nodes.CodeSpanNode):
            r=document.createElement("code")
            r.appendChild(document.createTextNode("".join(node.content).decode("utf-8")))
            yield r
        elif isinstance(node,nodes.BoldNode):
            if node.emphatic:
                r=document.createElement("strong")
            else:
                r=document.createElement("b")
            for domn in html_out_part(node.content,document,flags=flags):
                r.appendChild(domn)
            yield r
        elif isinstance(node,nodes.ItalicNode):
            if node.emphatic:
                r=document.createElement("em")
            else:
                r=document.createElement("i")
            for domn in html_out_part(node.content,document,flags=flags):
                r.appendChild(domn)
            yield r
        elif isinstance(node,nodes.BadassEchoNode):
            r=document.createElement("i")
            r.setAttribute("href","https://www.youtube.com/watch?v=SQoA_wjmE9w")
            for domn in html_out_part(node.content,document,flags=flags):
                r.appendChild(domn)
            yield r
        elif isinstance(node,nodes.SuperNode):
            r=document.createElement("sup")
            for domn in html_out_part(node.content,document,flags=flags):
                r.appendChild(domn)
            yield r
        elif isinstance(node,nodes.SubscrNode):
            r=document.createElement("sub")
            for domn in html_out_part(node.content,document,flags=flags):
                r.appendChild(domn)
            yield r
        elif isinstance(node,nodes.RubiNode):
            content=node.content
            r=document.createElement("ruby")
            #r.setAttribute("lang","jp")
            r.appendChild(document.createTextNode(content.decode("utf-8")))
            rp1=document.createElement("rp")
            rp1.appendChild(document.createTextNode(" ("))
            r.appendChild(rp1)
            rt=document.createElement("rt")
            for domn in html_out_part(node.label,document):
                rt.appendChild(domn)
            r.appendChild(rt)
            rp2=document.createElement("rp")
            rp2.appendChild(document.createTextNode(") "))
            r.appendChild(rp2)
            yield r
        elif isinstance(node,nodes.HrefNode):
            ht=node.hreftype
            content=node.content
            if ht=="url":
                label=html_out_part(node.label,document)
                if ("showtropes" in flags) and re.match("https?://(www\.)?tvtropes.org",content):
                    metar=document.createElement("span")
                    r=document.createElement("u")
                    metar.appendChild(r)
                    for domn in label:
                        r.appendChild(domn)
                    r2=document.createElement("sup")
                    metar.appendChild(r2)
                    r3=document.createElement("a")
                    r2.appendChild(r3)
                    r3.setAttribute("href",content.decode("utf-8"))
                    r3.appendChild(document.createTextNode("(TVTropes)"))
                    yield metar
                    continue
                r=document.createElement("a")
                r.setAttribute("href",content.decode("utf-8"))
                for domn in label:
                    r.appendChild(domn)
                yield r
            elif "script" in ht:
                pass #No way, Jos{\'e}!
            else: #Including img
                try:
                    label="".join(node.label)
                except TypeError:
                    label=html_out_body(node.label) #_body, not _part
                r=document.createElement(ht)
                r.setAttribute("src",content.decode("utf-8"))
                if label:
                    r.setAttribute("alt",label.decode("utf-8"))
                styl=""
                if node.width:
                    styl+="width:%dpx;"%node.width
                if node.height:
                    styl+="height:%dpx;"%node.height
                if styl:
                    r.setAttribute("style",styl)
                if "//twemoji.maxcdn.com" in content:
                    # Acceptable attribution per https://github.com/twitter/twemoji/blob/b33c30e78db45be787410567ad6f4c7b56c137a0/README.md#attribution-requirements
                    yield document.createComment(" twemoji, by Twitter, Inc.  Licensed under CC-BY 4.0 (http://creativecommons.org/licenses/by/4.0/), available from https://github.com/twitter/twemoji/ ")
                yield r
        elif isinstance(node,nodes.NewlineNode):
            r=document.createElement("br")
            yield r
        elif isinstance(node,nodes.RuleNode):
            r=document.createElement("hr")
            yield r
        elif isinstance(node,nodes.TableNode):
            r=document.createElement("table")
            r.setAttribute("border","1")
            thead=document.createElement("thead")
            r.appendChild(thead)
            for row in node.table_head:
                tr=document.createElement("tr")
                thead.appendChild(tr)
                for colno,cell in enumerate(row):
                    th=document.createElement("th")
                    tr.appendChild(th)
                    if node.aligns and (len(node.aligns)>colno) and node.aligns[colno]:
                        th.setAttribute("style","text-align:"+node.aligns[colno])
                    for domn in html_out_part(list(cell),document):
                        th.appendChild(domn)
            tbody=document.createElement("tbody")
            r.appendChild(tbody)
            for row in node.table_body:
                tr=document.createElement("tr")
                tbody.appendChild(tr)
                for colno,cell in enumerate(row):
                    td=document.createElement("td")
                    tr.appendChild(td)
                    if node.aligns and (len(node.aligns)>colno) and node.aligns[colno]:
                        td.setAttribute("style","text-align:"+node.aligns[colno])
                    for domn in html_out_part(list(cell),document):
                        td.appendChild(domn)
            yield r
        elif isinstance(node,nodes.EmptyInterrupterNode):
            yield document.createTextNode("")
        else:
            yield document.createTextNode("ERROR"+repr(node))

#import htmlentitydefs
from mdplay import htmlentitydefs_latest as htmlentitydefs
def _escape(text,html5=0):
    text=text.decode("utf-8")
    if not html5:
        keys=htmlentitydefs.name2codepoint.keys()
    else:
        keys=htmlentitydefs.html5.keys()
    for name in keys:
        if name not in ("amp","lt","quot","gt"): #handled already by minidom and would mess up syntax
            if not html5:
                codept=unichr(htmlentitydefs.name2codepoint[name])
            else:
                codept=htmlentitydefs.html5[name]
            if (len(codept)==1) and (ord(codept)<0xff) and (name not in htmlentitydefs.name2codepoint):
                continue #or face insanity.
            text=text.replace(codept,("&"+name.rstrip(";")+";").decode("ascii"))
    return text.encode("utf-8")

def html_out(nodem,titl="",flags=()):
    if "fragment" in flags:
        return html_out_body(nodem,flags)
    html5=("html5" in flags)
    mdi=minidom.getDOMImplementation() #minidom: other xml.dom imps don't necessarily support toxml
    if not html5:
        document=mdi.createDocument("http://www.w3.org/1999/xhtml","html",mdi.createDocumentType("html","-//W3C//DTD XHTML 1.1//EN","http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"))
    else:
        document=mdi.createDocument("http://www.w3.org/1999/xhtml","html",mdi.createDocumentType("html",None,"about:legacy-compat"))
    document.documentElement.setAttribute("xmlns","http://www.w3.org/1999/xhtml") #ehem... minidom... ehem...
    head=document.createElement("head")
    document.documentElement.appendChild(head)
    body=document.createElement("body")
    document.documentElement.appendChild(body)
    #Head
    if titl:
        titlebar=document.createElement("title")
        head.appendChild(titlebar)
        titlebar.appendChild(document.createTextNode(titl.decode("utf-8")))
    charset=document.createElement("meta")
    head.appendChild(charset)
    if not html5:
        charset.setAttribute("http-equiv","Content-Type")
        charset.setAttribute("content","text/html; charset=UTF-8")
    else:
        charset.setAttribute("charset","UTF-8")
        xua=document.createElement("meta")
        head.appendChild(xua)
        xua.setAttribute("http-equiv","X-UA-Compatible")
        xua.setAttribute("content","IE=10,chrome=1")
    #Body
    nodem=list(nodem)
    for domn in html_out_part(nodem,document,flags=flags):
        body.appendChild(domn)
    retval=_escape(document.toxml("utf-8"),html5)
    document.unlink()
    return retval

def html_out_body(nodem,flags=()):
    html5=("html5" in flags)
    mdi=minidom.getDOMImplementation() #minidom: other xml.dom imps don't necessarily support toxml
    document=mdi.createDocument("http://www.w3.org/1999/xhtml","html",mdi.createDocumentType("html","-//W3C//DTD XHTML 1.1//EN","http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd")) #never actually seen.
    ret=""
    nodem=list(nodem)
    for domn in html_out_part(nodem,document,flags=flags):
        ret+=domn.toxml("utf-8")
    document.unlink()
    return _escape(ret,html5)

__mdplay_renderer__="html_out"
__mdplay_snippet_renderer__="html_out_body"
