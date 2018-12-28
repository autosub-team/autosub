# -*- coding: utf-8 -*-

def BUTTON_TO(name, uri, confirm=None, style="display:inline;margin:0px;", target=None):
    if target:
        c = confirm and ("return confirm(\"%s\");" % confirm) or ''
        f = FORM(INPUT(_type="submit",_value=name),
                _style=style,
                _onclick="javascript:" + c + target + ".location='" + uri +"';return false;")
    else:
        f = FORM(INPUT(_type="submit",_value=name),
                _style=style, _action=uri,
                _onclick=confirm and ("javascript:return confirm(\"%s\")" % confirm) or None)
    return f


