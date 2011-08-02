import cgi
import htmlentitydefs
import urllib
import re
__all__ = ['html_quote',
 'html_unquote',
 'url_quote',
 'url_unquote',
 'strip_html']
default_encoding = 'UTF-8'

def html_quote(v, encoding = None):
    encoding = encoding or default_encoding
    if v is None:
        return ''
    else:
        if isinstance(v, str):
            return cgi.escape(v, 1)
        if isinstance(v, unicode):
            return cgi.escape(v.encode(encoding), 1)
        return cgi.escape(unicode(v).encode(encoding), 1)


_unquote_re = re.compile('&([a-zA-Z]+);')

def _entity_subber(match, name2c = htmlentitydefs.name2codepoint):
    code = name2c.get(match.group(1))
    if code:
        return unichr(code)
    else:
        return match.group(0)



def html_unquote(s, encoding = None):
    if isinstance(s, str):
        if s == '':
            return u''
        s = s.decode(encoding or default_encoding)
    return _unquote_re.sub(_entity_subber, s)



def strip_html(s):
    s = re.sub('<.*?>', '', s)
    s = html_unquote(s)
    return s



def no_quote(s):
    return s


_comment_quote_re = re.compile('\\-\\s*\\>')
_bad_chars_re = re.compile('[\x00-\x08\x0b-\x0c\x0e-\x1f]')

def comment_quote(s):
    comment = str(s)
    comment = _comment_quote_re.sub('-&gt;', comment)
    return comment


url_quote = urllib.quote
url_unquote = urllib.unquote
if __name__ == '__main__':
    import doctest
    doctest.testmod()

