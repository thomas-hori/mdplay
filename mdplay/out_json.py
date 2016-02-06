import re
try:
    import json
except:
    import simplejson as json

from mdplay import nodes

def json_out(nodes,titl_ignored=None,flags=()):
    return json_out_body(nodes,flags=flags)

def json_out_body(nodes,flags=()):
    return json.dumps(_json_out_body(nodes,flags=flags))

def _json_out_body(nodes,flags=()):
    in_list=0
    r=[]
    for node in nodes:
        r.append(_json_out(node,flags=flags))
    return r

def _json_out(node,flags):
    if not isinstance(node,nodes.Node): #i.e. is a string
        return node
    else:
        dci=node.__dict__
        dco={}
        dco["NODE_TYPE"]=node.__class__.__name__
        for i in dci.keys():
            if i[0]!="_":
                if i in ("content","label"):
                    dco[i]=map(_json_out,dci[i],[flags]*len(dci[i]))
                elif i in ("table_head","table_body"):
                    dco[i]=[]
                    for j in dci[i]:
                        dco[i].append([])
                        for k in j:
                            dco[i][-1].append(map(_json_out,k,[flags]*len(k)))
                else:
                    dco[i]=dci[i]
        return dco

__mdplay_renderer__="json_out"
__mdplay_snippet_renderer__="json_out_body"
