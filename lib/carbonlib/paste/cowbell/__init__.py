import os
import re
from paste.fileapp import FileApp
from paste.response import header_value, remove_header
SOUND = 'http://www.c-eye.net/eyeon/WalkenWAVS/explorestudiospace.wav'

class MoreCowbell(object):

    def __init__(self, app):
        self.app = app



    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        script_name = environ.get('SCRIPT_NAME', '')
        for filename in ['bell-ascending.png', 'bell-descending.png']:
            if path_info == '/.cowbell/' + filename:
                app = FileApp(os.path.join(os.path.dirname(__file__), filename))
                return app(environ, start_response)

        type = []
        body = []

        def repl_start_response(status, headers, exc_info = None):
            ct = header_value(headers, 'content-type')
            if ct and ct.startswith('text/html'):
                type.append(ct)
                remove_header(headers, 'content-length')
                start_response(status, headers, exc_info)
                return body.append
            return start_response(status, headers, exc_info)


        app_iter = self.app(environ, repl_start_response)
        if type:
            body.extend(app_iter)
            body = ''.join(body)
            body = insert_head(body, self.javascript.replace('__SCRIPT_NAME__', script_name))
            body = insert_body(body, self.resources.replace('__SCRIPT_NAME__', script_name))
            return [body]
        else:
            return app_iter


    javascript = '<script type="text/javascript">\nvar cowbellState = \'hidden\';\nvar lastCowbellPosition = null;\nfunction showSomewhere() {\n  var sec, el;\n  if (cowbellState == \'hidden\') {\n    el = document.getElementById(\'cowbell-ascending\');\n    lastCowbellPosition = [parseInt(Math.random()*(window.innerWidth-200)), \n                           parseInt(Math.random()*(window.innerHeight-200))];\n    el.style.left = lastCowbellPosition[0] + \'px\';\n    el.style.top = lastCowbellPosition[1] + \'px\';\n    el.style.display = \'\';\n    cowbellState = \'ascending\';\n    sec = 1;\n  } else if (cowbellState == \'ascending\') {\n    document.getElementById(\'cowbell-ascending\').style.display = \'none\';\n    el = document.getElementById(\'cowbell-descending\');\n    el.style.left = lastCowbellPosition[0] + \'px\';\n    el.style.top = lastCowbellPosition[1] + \'px\';\n    el.style.display = \'\';\n    cowbellState = \'descending\';\n    sec = 1;\n  } else {\n    document.getElementById(\'cowbell-descending\').style.display = \'none\';\n    cowbellState = \'hidden\';\n    sec = Math.random()*20;\n  }\n  setTimeout(showSomewhere, sec*1000);\n}\nsetTimeout(showSomewhere, Math.random()*20*1000);\n</script>\n'
    resources = '<div id="cowbell-ascending" style="display: none; position: fixed">\n<img src="__SCRIPT_NAME__/.cowbell/bell-ascending.png">\n</div>\n<div id="cowbell-descending" style="display: none; position: fixed">\n<img src="__SCRIPT_NAME__/.cowbell/bell-descending.png">\n</div>\n'


def insert_head(body, text):
    end_head = re.search('</head>', body, re.I)
    if end_head:
        return body[:end_head.start()] + text + body[end_head.end():]
    else:
        return text + body



def insert_body(body, text):
    end_body = re.search('</body>', body, re.I)
    if end_body:
        return body[:end_body.start()] + text + body[end_body.end():]
    else:
        return body + text



def make_cowbell(global_conf, app):
    return MoreCowbell(app)


if __name__ == '__main__':
    from paste.debug.debugapp import SimpleApplication
    app = MoreCowbell(SimpleApplication())
    from paste.httpserver import serve
    serve(app)

