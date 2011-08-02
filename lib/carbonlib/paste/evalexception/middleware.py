import sys
import os
import cgi
import traceback
from cStringIO import StringIO
import pprint
import itertools
import time
import re
from paste.exceptions import errormiddleware, formatter, collector
from paste import wsgilib
from paste import urlparser
from paste import httpexceptions
from paste import registry
from paste import request
from paste import response
import evalcontext
limit = 200

def html_quote(v):
    if v is None:
        return ''
    return cgi.escape(str(v), 1)



def preserve_whitespace(v, quote = True):
    if quote:
        v = html_quote(v)
    v = v.replace('\n', '<br>\n')
    v = re.sub('()(  +)', _repl_nbsp, v)
    v = re.sub('(\\n)( +)', _repl_nbsp, v)
    v = re.sub('^()( +)', _repl_nbsp, v)
    return '<code>%s</code>' % v



def _repl_nbsp(match):
    if len(match.group(2)) == 1:
        return '&nbsp;'
    return match.group(1) + '&nbsp;' * (len(match.group(2)) - 1) + ' '



def simplecatcher(application):

    def simplecatcher_app(environ, start_response):
        try:
            return application(environ, start_response)
        except:
            out = StringIO()
            traceback.print_exc(file=out)
            start_response('500 Server Error', [('content-type', 'text/html')], sys.exc_info())
            res = out.getvalue()
            return ['<h3>Error</h3><pre>%s</pre>' % html_quote(res)]


    return simplecatcher_app



def wsgiapp():

    def decorator(func):

        def wsgiapp_wrapper(*args):
            if len(args) == 3:
                environ = args[1]
                start_response = args[2]
                args = [args[0]]
            else:
                (environ, start_response,) = args
                args = []

            def application(environ, start_response):
                form = wsgilib.parse_formvars(environ, include_get_vars=True)
                headers = response.HeaderDict({'content-type': 'text/html',
                 'status': '200 OK'})
                form['environ'] = environ
                form['headers'] = headers
                res = func(*args, **form.mixed())
                status = headers.pop('status')
                start_response(status, headers.headeritems())
                return [res]


            app = httpexceptions.make_middleware(application)
            app = simplecatcher(app)
            return app(environ, start_response)


        wsgiapp_wrapper.exposed = True
        return wsgiapp_wrapper


    return decorator



def get_debug_info(func):

    def debug_info_replacement(self, **form):
        try:
            if 'debugcount' not in form:
                raise ValueError('You must provide a debugcount parameter')
            debugcount = form.pop('debugcount')
            try:
                debugcount = int(debugcount)
            except ValueError:
                raise ValueError('Bad value for debugcount')
            if debugcount not in self.debug_infos:
                raise ValueError('Debug %s no longer found (maybe it has expired?)' % debugcount)
            debug_info = self.debug_infos[debugcount]
            return func(self, debug_info=debug_info, **form)
        except ValueError as e:
            form['headers']['status'] = '500 Server Error'
            return '<html>There was an error: %s</html>' % html_quote(e)


    return debug_info_replacement


debug_counter = itertools.count(int(time.time()))

def get_debug_count(environ):
    if 'paste.evalexception.debug_count' in environ:
        return environ['paste.evalexception.debug_count']
    else:
        environ['paste.evalexception.debug_count'] = next = debug_counter.next()
        return next



class EvalException(object):

    def __init__(self, application, global_conf = None, xmlhttp_key = None):
        self.application = application
        self.debug_infos = {}
        if xmlhttp_key is None:
            if global_conf is None:
                xmlhttp_key = '_'
            else:
                xmlhttp_key = global_conf.get('xmlhttp_key', '_')
        self.xmlhttp_key = xmlhttp_key



    def __call__(self, environ, start_response):
        environ['paste.evalexception'] = self
        if environ.get('PATH_INFO', '').startswith('/_debug/'):
            return self.debug(environ, start_response)
        else:
            return self.respond(environ, start_response)



    def debug(self, environ, start_response):
        next_part = request.path_info_pop(environ)
        method = getattr(self, next_part, None)
        if not method:
            exc = httpexceptions.HTTPNotFound('%r not found when parsing %r' % (next_part, wsgilib.construct_url(environ)))
            return exc.wsgi_application(environ, start_response)
        if not getattr(method, 'exposed', False):
            exc = httpexceptions.HTTPForbidden('%r not allowed' % next_part)
            return exc.wsgi_application(environ, start_response)
        return method(environ, start_response)



    def media(self, environ, start_response):
        app = urlparser.StaticURLParser(os.path.join(os.path.dirname(__file__), 'media'))
        return app(environ, start_response)


    media.exposed = True

    def mochikit(self, environ, start_response):
        app = urlparser.StaticURLParser(os.path.join(os.path.dirname(__file__), 'mochikit'))
        return app(environ, start_response)


    mochikit.exposed = True

    def summary(self, environ, start_response):
        start_response('200 OK', [('Content-type', 'text/x-json')])
        data = []
        items = self.debug_infos.values()
        items.sort(lambda a, b: cmp(a.created, b.created))
        data = [ item.json() for item in items ]
        return [repr(data)]


    summary.exposed = True

    def view(self, environ, start_response):
        id = int(request.path_info_pop(environ))
        if id not in self.debug_infos:
            start_response('500 Server Error', [('Content-type', 'text/html')])
            return ['Traceback by id %s does not exist (maybe the server has been restarted?)' % id]
        debug_info = self.debug_infos[id]
        return debug_info.wsgi_application(environ, start_response)


    view.exposed = True

    def make_view_url(self, environ, base_path, count):
        return base_path + '/_debug/view/%s' % count



    def show_frame(self, tbid, debug_info, **kw):
        frame = debug_info.frame(int(tbid))
        vars = frame.tb_frame.f_locals
        if vars:
            registry.restorer.restoration_begin(debug_info.counter)
            local_vars = make_table(vars)
            registry.restorer.restoration_end()
        else:
            local_vars = 'No local vars'
        return input_form(tbid, debug_info) + local_vars


    show_frame = wsgiapp()(get_debug_info(show_frame))

    def exec_input(self, tbid, debug_info, input, **kw):
        if not input.strip():
            return ''
        input = input.rstrip() + '\n'
        frame = debug_info.frame(int(tbid))
        vars = frame.tb_frame.f_locals
        glob_vars = frame.tb_frame.f_globals
        context = evalcontext.EvalContext(vars, glob_vars)
        registry.restorer.restoration_begin(debug_info.counter)
        output = context.exec_expr(input)
        registry.restorer.restoration_end()
        input_html = formatter.str2html(input)
        return '<code style="color: #060">&gt;&gt;&gt;</code> <code>%s</code><br>\n%s' % (preserve_whitespace(input_html, quote=False), preserve_whitespace(output))


    exec_input = wsgiapp()(get_debug_info(exec_input))

    def respond(self, environ, start_response):
        if environ.get('paste.throw_errors'):
            return self.application(environ, start_response)
        base_path = request.construct_url(environ, with_path_info=False, with_query_string=False)
        environ['paste.throw_errors'] = True
        started = []

        def detect_start_response(status, headers, exc_info = None):
            try:
                return start_response(status, headers, exc_info)
            except:
                raise 
            else:
                started.append(True)


        try:
            __traceback_supplement__ = (errormiddleware.Supplement, self, environ)
            app_iter = self.application(environ, detect_start_response)
            try:
                return_iter = list(app_iter)
                return return_iter

            finally:
                if hasattr(app_iter, 'close'):
                    app_iter.close()

        except:
            exc_info = sys.exc_info()
            for expected in environ.get('paste.expected_exceptions', []):
                if isinstance(exc_info[1], expected):
                    raise 

            registry.restorer.save_registry_state(environ)
            count = get_debug_count(environ)
            view_uri = self.make_view_url(environ, base_path, count)
            if not started:
                headers = [('content-type', 'text/html')]
                headers.append(('X-Debug-URL', view_uri))
                start_response('500 Internal Server Error', headers, exc_info)
            environ['wsgi.errors'].write('Debug at: %s\n' % view_uri)
            exc_data = collector.collect_exception(*exc_info)
            debug_info = DebugInfo(count, exc_info, exc_data, base_path, environ, view_uri)
            self.debug_infos[count] = debug_info
            if self.xmlhttp_key:
                get_vars = wsgilib.parse_querystring(environ)
                if dict(get_vars).get(self.xmlhttp_key):
                    exc_data = collector.collect_exception(*exc_info)
                    html = formatter.format_html(exc_data, include_hidden_frames=False, include_reusable=False, show_extra_data=False)
                    return [html]
            return debug_info.content()



    def exception_handler(self, exc_info, environ):
        simple_html_error = False
        if self.xmlhttp_key:
            get_vars = wsgilib.parse_querystring(environ)
            if dict(get_vars).get(self.xmlhttp_key):
                simple_html_error = True
        return errormiddleware.handle_exception(exc_info, environ['wsgi.errors'], html=True, debug_mode=True, simple_html_error=simple_html_error)




class DebugInfo(object):

    def __init__(self, counter, exc_info, exc_data, base_path, environ, view_uri):
        self.counter = counter
        self.exc_data = exc_data
        self.base_path = base_path
        self.environ = environ
        self.view_uri = view_uri
        self.created = time.time()
        (self.exc_type, self.exc_value, self.tb,) = exc_info
        __exception_formatter__ = 1
        self.frames = []
        n = 0
        tb = self.tb
        while tb is not None and (limit is None or n < limit):
            if tb.tb_frame.f_locals.get('__exception_formatter__'):
                break
            self.frames.append(tb)
            tb = tb.tb_next
            n += 1




    def json(self):
        return {'uri': self.view_uri,
         'created': time.strftime('%c', time.gmtime(self.created)),
         'created_timestamp': self.created,
         'exception_type': str(self.exc_type),
         'exception': str(self.exc_value)}



    def frame(self, tbid):
        for frame in self.frames:
            if id(frame) == tbid:
                return frame
        else:
            raise ValueError, 'No frame by id %s found from %r' % (tbid, self.frames)




    def wsgi_application(self, environ, start_response):
        start_response('200 OK', [('content-type', 'text/html')])
        return self.content()



    def content(self):
        html = format_eval_html(self.exc_data, self.base_path, self.counter)
        head_html = formatter.error_css + formatter.hide_display_js
        head_html += self.eval_javascript()
        repost_button = make_repost_button(self.environ)
        page = error_template % {'repost_button': repost_button or '',
         'head_html': head_html,
         'body': html}
        return [page]



    def eval_javascript(self):
        base_path = self.base_path + '/_debug'
        return '<script type="text/javascript" src="%s/media/MochiKit.packed.js"></script>\n<script type="text/javascript" src="%s/media/debug.js"></script>\n<script type="text/javascript">\ndebug_base = %r;\ndebug_count = %r;\n</script>\n' % (base_path,
         base_path,
         base_path,
         self.counter)




class EvalHTMLFormatter(formatter.HTMLFormatter):

    def __init__(self, base_path, counter, **kw):
        super(EvalHTMLFormatter, self).__init__(**kw)
        self.base_path = base_path
        self.counter = counter



    def format_source_line(self, filename, frame):
        line = formatter.HTMLFormatter.format_source_line(self, filename, frame)
        return line + '  <a href="#" class="switch_source" tbid="%s" onClick="return showFrame(this)">&nbsp; &nbsp; <img src="%s/_debug/media/plus.jpg" border=0 width=9 height=9> &nbsp; &nbsp;</a>' % (frame.tbid, self.base_path)




def make_table(items):
    if isinstance(items, dict):
        items = items.items()
        items.sort()
    rows = []
    i = 0
    for (name, value,) in items:
        i += 1
        out = StringIO()
        try:
            pprint.pprint(value, out)
        except Exception as e:
            print >> out, 'Error: %s' % e
        value = html_quote(out.getvalue())
        if len(value) > 100:
            orig_value = value
            value = value[:100]
            value += '<a class="switch_source" style="background-color: #999" href="#" onclick="return expandLong(this)">...</a>'
            value += '<span style="display: none">%s</span>' % orig_value[100:]
        value = formatter.make_wrappable(value)
        if i % 2:
            attr = ' class="even"'
        else:
            attr = ' class="odd"'
        rows.append('<tr%s style="vertical-align: top;"><td><b>%s</b></td><td style="overflow: auto">%s<td></tr>' % (attr, html_quote(name), preserve_whitespace(value, quote=False)))

    return '<table>%s</table>' % '\n'.join(rows)



def format_eval_html(exc_data, base_path, counter):
    short_formatter = EvalHTMLFormatter(base_path=base_path, counter=counter, include_reusable=False)
    short_er = short_formatter.format_collected_data(exc_data)
    long_formatter = EvalHTMLFormatter(base_path=base_path, counter=counter, show_hidden_frames=True, show_extra_data=False, include_reusable=False)
    long_er = long_formatter.format_collected_data(exc_data)
    text_er = formatter.format_text(exc_data, show_hidden_frames=True)
    if short_formatter.filter_frames(exc_data.frames) != long_formatter.filter_frames(exc_data.frames):
        full_traceback_html = '\n    <br>\n    <script type="text/javascript">\n    show_button(\'full_traceback\', \'full traceback\')\n    </script>\n    <div id="full_traceback" class="hidden-data">\n    %s\n    </div>\n        ' % long_er
    else:
        full_traceback_html = ''
    return '\n    %s\n    %s\n    <br>\n    <script type="text/javascript">\n    show_button(\'text_version\', \'text version\')\n    </script>\n    <div id="text_version" class="hidden-data">\n    <textarea style="width: 100%%" rows=10 cols=60>%s</textarea>\n    </div>\n    ' % (short_er, full_traceback_html, cgi.escape(text_er))



def make_repost_button(environ):
    url = request.construct_url(environ)
    if environ['REQUEST_METHOD'] == 'GET':
        return '<button onclick="window.location.href=%r">Re-GET Page</button><br>' % url
    else:
        return None



def input_form(tbid, debug_info):
    return '\n<form action="#" method="POST"\n onsubmit="return submitInput($(\'submit_%(tbid)s\'), %(tbid)s)">\n<div id="exec-output-%(tbid)s" style="width: 95%%;\n padding: 5px; margin: 5px; border: 2px solid #000;\n display: none"></div>\n<input type="text" name="input" id="debug_input_%(tbid)s"\n style="width: 100%%"\n autocomplete="off" onkeypress="upArrow(this, event)"><br>\n<input type="submit" value="Execute" name="submitbutton"\n onclick="return submitInput(this, %(tbid)s)"\n id="submit_%(tbid)s"\n input-from="debug_input_%(tbid)s"\n output-to="exec-output-%(tbid)s">\n<input type="submit" value="Expand"\n onclick="return expandInput(this)">\n</form>\n ' % {'tbid': tbid}


error_template = '\n<html>\n<head>\n <title>Server Error</title>\n %(head_html)s\n</head>\n<body>\n\n<div id="error-area" style="display: none; background-color: #600; color: #fff; border: 2px solid black">\n<div id="error-container"></div>\n<button onclick="return clearError()">clear this</button>\n</div>\n\n%(repost_button)s\n\n%(body)s\n\n</body>\n</html>\n'

def make_eval_exception(app, global_conf, xmlhttp_key = None):
    if xmlhttp_key is None:
        xmlhttp_key = global_conf.get('xmlhttp_key', '_')
    return EvalException(app, xmlhttp_key=xmlhttp_key)



