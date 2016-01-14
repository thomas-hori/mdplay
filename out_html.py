import re
from xml.dom import minidom

import nodes

def html_out_body(nodem,document,in_list=0):
    return list(_html_out_body(nodem,document,in_list))

def _html_out_body(nodem,document,in_list=0):
    while nodem:
        node=nodem.pop(0)
        if isinstance(node,nodes.UlliNode):
            if (node.depth+1)>in_list:
                r=document.createElement("ul")
                r2=document.createElement("li")
                r.appendChild(r2)
                for domn in html_out_body(node.content,document):
                    r2.appendChild(domn)
                for domn in html_out_body(nodem,document,in_list+1):
                    r.appendChild(domn)
                yield r
            elif (node.depth+1)<in_list:
                nodem.insert(0,node)
                return
            else:
                r=document.createElement("li")
                for domn in html_out_body(node.content,document):
                    r.appendChild(domn)
                yield r
        elif in_list: #A non-list node at list-stack level
            nodem.insert(0,node)
            return
        elif not isinstance(node,nodes.Node): #i.e. is a string
            yield document.createTextNode(node.decode("utf-8"))
        elif isinstance(node,nodes.TitleNode):
            if node.depth>6: node.depth=6
            r=document.createElement("h%d"%node.depth)
            for domn in html_out_body(node.content,document):
                r.appendChild(domn)
            yield r
        elif isinstance(node,nodes.ParagraphNode):
            r=document.createElement("p")
            for domn in html_out_body(node.content,document):
                r.appendChild(domn)
            yield r
        elif isinstance(node,nodes.BlockQuoteNode):
            r=document.createElement("blockquote")
            for domn in html_out_body(node.content,document):
                r.appendChild(domn)
            yield r
        #elif isinstance(node,nodes.SpoilerNode):
        #    yield "<p><a href='javascript:void(0);' onclick=\"document.getElementById('spoil%d').style.display=(document.getElementById('spoil%d').style.display=='none')?('block'):('none')\">Expand/Hide Spoiler</a></p><div class='spoiler' id='spoil%d' style='display:none;'>"%(id(node),id(node),id(node))+html_out_body(node.content,document)+"</div>"
        elif isinstance(node,nodes.SpoilerNode):
            metar=document.createElement("div")
            metar.setAttribute("class",'spoilerwrapper')
            r=document.createElement("p")
            metar.appendChild(r)
            r2=document.createElement("a")
            r.appendChild(r2)
            r2.setAttribute("href",'javascript:void(0);')
            r2.setAttribute("onclick","document.getElementById('spoil%d').style.display=(document.getElementById('spoil%d').style.display=='none')?('block'):('none')"%(id(node),id(node)))
            r2.appendChild(document.createTextNode("Expand/Hide Spoiler"))
            r3=document.createElement("div")
            metar.appendChild(r3)
            r3.setAttribute("class",'spoiler')
            r3.setAttribute("id",'spoil%d'%id(node))
            r3.setAttribute("style",'display:none;')
            for domn in html_out_body(node.content,document):
                r3.appendChild(domn)
            yield metar
        elif isinstance(node,nodes.CodeBlockNode):
            r=document.createElement("pre")
            r.appendChild(document.createTextNode("".join(node.content)))
            yield r
        elif isinstance(node,nodes.BoldNode):
            if node.emphatic:
                r=document.createElement("strong")
            else:
                r=document.createElement("b")
            for domn in html_out_body(node.content,document):
                r.appendChild(domn)
            yield r
        elif isinstance(node,nodes.ItalicNode):
            if node.emphatic:
                r=document.createElement("em")
            else:
                r=document.createElement("i")
            for domn in html_out_body(node.content,document):
                r.appendChild(domn)
            yield r
        elif isinstance(node,nodes.SuperNode):
            r=document.createElement("sup")
            for domn in html_out_body(node.content,document):
                r.appendChild(domn)
            yield r
        elif isinstance(node,nodes.SubscrNode):
            r=document.createElement("sub")
            for domn in html_out_body(node.content,document):
                r.appendChild(domn)
            yield r
        elif isinstance(node,nodes.HrefNode):
            ht=node.hreftype
            content=node.content
            if ht=="url":
                label=html_out_body(node.label,document)
                if re.match("https?://(www\.)?tvtropes.org",content):
                    metar=document.createElement("span")
                    r=document.createElement("u")
                    metar.appendChild(r)
                    for domn in label:
                        r.appendChild(domn)
                    r2=document.createElement("sup")
                    metar.appendChild(r2)
                    r3=document.createElement("a")
                    r2.appendChild(r3)
                    r3.setAttribute("href",content)
                    r3.appendChild(document.createTextNode("(TVTropes)"))
                    yield metar
                    continue
                r=document.createElement("a")
                r.setAttribute("href",content)
                for domn in label:
                    r.appendChild(domn)
                yield r
            else: #Including img
                label="".join(node.label)
                r=document.createElement(ht)
                r.setAttribute("src",content)
                if label:
                    r.setAttribute("alt",label)
                yield r
        elif isinstance(node,nodes.NewlineNode):
            r=document.createElement("br")
            yield r
        elif isinstance(node,nodes.RuleNode):
            r=document.createElement("hr")
            yield r
        else:
            yield document.createTextNode("ERROR"+repr(node))

def html_out(nodes,titl=""):
    mdi=minidom.getDOMImplementation()
    document=mdi.createDocument("http://www.w3.org/1999/xhtml","html",mdi.createDocumentType("html","-//W3C//DTD XHTML 1.1//EN","http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"))
    head=document.createElement("head")
    document.documentElement.appendChild(head)
    body=document.createElement("body")
    document.documentElement.appendChild(body)
    #Head
    if titl:
        titlebar=document.createElement("title")
        head.appendChild(titlebar)
        titlebar.appendChild(document.createTextNode(titl))
    charset=document.createElement("meta")
    head.appendChild(charset)
    charset.setAttribute("http-equiv","Content-Type")
    charset.setAttribute("content","text/html; charset=UTF-8")
    #Body
    nodes=list(nodes)
    for domn in html_out_body(nodes,document):
        body.appendChild(domn)
    return document.toxml("utf-8")

