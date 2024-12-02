from urllib.parse import urlparse

def return_url(request, params={}):
    """
    Da la url que corresponde a la página anterior en la que estaba el usuario.
    Si la ultima pagina y la actual son la misma, da la pagina principal.
    Recibe un Request de Django, y opcionalmente un diccionario de parametros que añadir
    """

    def query_str(base_maybe, params={}):
        # la idea de esta funcion auxiliar es juntar los parametros que pueda traer
        # la url con los especificados en el diccionario param
        # /algo?a=b y {'c'='d'} => /algo?a=b&c=d
        # /algo?a=b y {'a'='d'} => /algo?a=b
        print(base_maybe, params)
        out = ""
        if base_maybe:
            out+=f"?{base_maybe}"
            for key, value in params.items():
                print(out.find(f"{key}="))
                if out.find(f"{key}=") == -1:
                    out+=f"&{key}={value}"
        else:
            i = 0
            for key, value in params.items():
                if out.find(f"{key}=") == -1:
                    if i==0:
                        out+=f"?{key}={value}"
                    else:
                        out+=f"&{key}={value}"
        return out

    # por default, pagina principal
    path = '/'+query_str("", params)

    if request.POST.get('goto'):
        # si hay goto en post, usa eso
        goto = urlparse(request.POST.get('goto'))
        path = goto.path+query_str(goto.query, params)
    elif request.META['HTTP_REFERER']:
        # Si no hay goto pero hay referrer, usa referrer
        meta = urlparse(request.META['HTTP_REFERER'])
        path = meta.path+query_str(meta.query, params)
    # si esta mandando a la actual, manda a la principal
    # para evitar loops de redireccionamiento
    if path == request.get_full_path():
        path = '/'+query_str("", params)
    return path