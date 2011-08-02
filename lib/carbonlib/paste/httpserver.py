import atexit
import traceback
import socket
import sys
import threading
import urlparse
import Queue
import urllib
import posixpath
import time
import thread
import os
from itertools import count
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
from paste.util import converters
import logging
try:
    from paste.util import killthread
except ImportError:
    killthread = None
__all__ = ['WSGIHandlerMixin',
 'WSGIServer',
 'WSGIHandler',
 'serve']
__version__ = '0.5'

class ContinueHook(object):

    def __init__(self, rfile, write):
        self._ContinueFile_rfile = rfile
        self._ContinueFile_write = write
        for attr in ('close', 'closed', 'fileno', 'flush', 'mode', 'bufsize', 'softspace'):
            if hasattr(rfile, attr):
                setattr(self, attr, getattr(rfile, attr))

        for attr in ('read', 'readline', 'readlines'):
            if hasattr(rfile, attr):
                setattr(self, attr, getattr(self, '_ContinueFile_' + attr))




    def _ContinueFile_send(self):
        self._ContinueFile_write('HTTP/1.1 100 Continue\r\n\r\n')
        rfile = self._ContinueFile_rfile
        for attr in ('read', 'readline', 'readlines'):
            if hasattr(rfile, attr):
                setattr(self, attr, getattr(rfile, attr))




    def _ContinueFile_read(self, size = -1):
        self._ContinueFile_send()
        return self._ContinueFile_rfile.read(size)



    def _ContinueFile_readline(self, size = -1):
        self._ContinueFile_send()
        return self._ContinueFile_rfile.readline(size)



    def _ContinueFile_readlines(self, sizehint = 0):
        self._ContinueFile_send()
        return self._ContinueFile_rfile.readlines(sizehint)




class WSGIHandlerMixin():
    lookup_addresses = True

    def log_request(self, *args, **kwargs):
        pass



    def log_message(self, *args, **kwargs):
        pass



    def version_string(self):
        if not self.sys_version:
            return self.server_version
        else:
            return self.server_version + ' ' + self.sys_version



    def wsgi_write_chunk(self, chunk):
        if not self.wsgi_headers_sent and not self.wsgi_curr_headers:
            raise RuntimeError('Content returned before start_response called')
        if not self.wsgi_headers_sent:
            self.wsgi_headers_sent = True
            (status, headers,) = self.wsgi_curr_headers
            (code, message,) = status.split(' ', 1)
            self.send_response(int(code), message)
            send_close = True
            for (k, v,) in headers:
                lk = k.lower()
                if 'content-length' == lk:
                    send_close = False
                if 'connection' == lk:
                    if 'close' == v.lower():
                        self.close_connection = 1
                        send_close = False
                self.send_header(k, v)

            if send_close:
                self.close_connection = 1
                self.send_header('Connection', 'close')
            self.end_headers()
        self.wfile.write(chunk)



    def wsgi_start_response(self, status, response_headers, exc_info = None):
        if exc_info:
            try:
                if self.wsgi_headers_sent:
                    raise exc_info[0], exc_info[1], exc_info[2]

            finally:
                exc_info = None

        elif self.wsgi_curr_headers:
            pass
        self.wsgi_curr_headers = (status, response_headers)
        return self.wsgi_write_chunk



    def wsgi_setup(self, environ = None):
        (scheme, netloc, path, query, fragment,) = urlparse.urlsplit(self.path)
        path = urllib.unquote(path)
        endslash = path.endswith('/')
        path = posixpath.normpath(path)
        if endslash and path != '/':
            path += '/'
        (server_name, server_port,) = self.server.server_address[:2]
        rfile = self.rfile
        if 'HTTP/1.1' == self.protocol_version and '100-continue' == self.headers.get('Expect', '').lower():
            rfile = ContinueHook(rfile, self.wfile.write)
        else:
            try:
                content_length = int(self.headers.get('Content-Length', '0'))
            except ValueError:
                content_length = 0
            if not hasattr(self.connection, 'get_context'):
                rfile = LimitedLengthFile(rfile, content_length)
        remote_address = self.client_address[0]
        self.wsgi_environ = {'wsgi.version': (1, 0),
         'wsgi.url_scheme': 'http',
         'wsgi.input': rfile,
         'wsgi.errors': sys.stderr,
         'wsgi.multithread': True,
         'wsgi.multiprocess': False,
         'wsgi.run_once': False,
         'REQUEST_METHOD': self.command,
         'SCRIPT_NAME': '',
         'PATH_INFO': path,
         'QUERY_STRING': query,
         'CONTENT_TYPE': self.headers.get('Content-Type', ''),
         'CONTENT_LENGTH': self.headers.get('Content-Length', '0'),
         'SERVER_NAME': server_name,
         'SERVER_PORT': str(server_port),
         'SERVER_PROTOCOL': self.request_version,
         'REMOTE_ADDR': remote_address}
        if scheme:
            self.wsgi_environ['paste.httpserver.proxy.scheme'] = scheme
        if netloc:
            self.wsgi_environ['paste.httpserver.proxy.host'] = netloc
        if self.lookup_addresses:
            if remote_address.startswith('192.168.') or remote_address.startswith('10.') or remote_address.startswith('172.16.'):
                pass
            else:
                address_string = None
                if address_string:
                    self.wsgi_environ['REMOTE_HOST'] = address_string
        if hasattr(self.server, 'thread_pool'):
            self.server.thread_pool.worker_tracker[thread.get_ident()][1] = self.wsgi_environ
            self.wsgi_environ['paste.httpserver.thread_pool'] = self.server.thread_pool
        for (k, v,) in self.headers.items():
            key = 'HTTP_' + k.replace('-', '_').upper()
            if key in ('HTTP_CONTENT_TYPE', 'HTTP_CONTENT_LENGTH'):
                continue
            self.wsgi_environ[key] = ','.join(self.headers.getheaders(k))

        if hasattr(self.connection, 'get_context'):
            self.wsgi_environ['wsgi.url_scheme'] = 'https'
        if environ:
            self.wsgi_environ.update(environ)
            if 'on' == environ.get('HTTPS'):
                self.wsgi_environ['wsgi.url_scheme'] = 'https'
        self.wsgi_curr_headers = None
        self.wsgi_headers_sent = False



    def wsgi_connection_drop(self, exce, environ = None):
        pass



    def wsgi_execute(self, environ = None):
        self.wsgi_setup(environ)
        try:
            result = self.server.wsgi_application(self.wsgi_environ, self.wsgi_start_response)
            try:
                for chunk in result:
                    self.wsgi_write_chunk(chunk)

                if not self.wsgi_headers_sent:
                    self.wsgi_write_chunk('')

            finally:
                if hasattr(result, 'close'):
                    result.close()
                result = None

        except socket.error as exce:
            self.wsgi_connection_drop(exce, environ)
            return 
        except:
            if not self.wsgi_headers_sent:
                error_msg = 'Internal Server Error\n'
                self.wsgi_curr_headers = ('500 Internal Server Error', [('Content-type', 'text/plain'), ('Content-length', str(len(error_msg)))])
                self.wsgi_write_chunk('Internal Server Error\n')
            raise 



try:
    from OpenSSL import SSL, tsafe
    SocketErrors = (socket.error, SSL.ZeroReturnError, SSL.SysCallError)
except ImportError:
    SSL = None
    SocketErrors = (socket.error,)

    class SecureHTTPServer(HTTPServer):

        def __init__(self, server_address, RequestHandlerClass, ssl_context = None, request_queue_size = None):
            HTTPServer.__init__(self, server_address, RequestHandlerClass)
            if request_queue_size:
                self.socket.listen(request_queue_size)



else:

    class _ConnFixer(object):

        def __init__(self, conn):
            self._ConnFixer__conn = conn



        def makefile(self, mode, bufsize):
            return socket._fileobject(self._ConnFixer__conn, mode, bufsize)



        def __getattr__(self, attrib):
            return getattr(self._ConnFixer__conn, attrib)




    class SecureHTTPServer(HTTPServer):

        def __init__(self, server_address, RequestHandlerClass, ssl_context = None, request_queue_size = None):
            HTTPServer.__init__(self, server_address, RequestHandlerClass)
            self.socket = socket.socket(self.address_family, self.socket_type)
            self.ssl_context = ssl_context
            if ssl_context:

                class TSafeConnection(tsafe.Connection):

                    def settimeout(self, *args):
                        self._lock.acquire()
                        try:
                            return self._ssl_conn.settimeout(*args)

                        finally:
                            self._lock.release()




                    def gettimeout(self):
                        self._lock.acquire()
                        try:
                            return self._ssl_conn.gettimeout()

                        finally:
                            self._lock.release()




                self.socket = TSafeConnection(ssl_context, self.socket)
            self.server_bind()
            if request_queue_size:
                self.socket.listen(request_queue_size)
            self.server_activate()



        def get_request(self):
            (conn, info,) = self.socket.accept()
            if self.ssl_context:
                conn = _ConnFixer(conn)
            return (conn, info)




    def _auto_ssl_context():
        import OpenSSL
        import time
        import random
        pkey = OpenSSL.crypto.PKey()
        pkey.generate_key(OpenSSL.crypto.TYPE_RSA, 768)
        cert = OpenSSL.crypto.X509()
        cert.set_serial_number(random.randint(0, sys.maxint))
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(31536000)
        cert.get_subject().CN = '*'
        cert.get_subject().O = 'Dummy Certificate'
        cert.get_issuer().CN = 'Untrusted Authority'
        cert.get_issuer().O = 'Self-Signed'
        cert.set_pubkey(pkey)
        cert.sign(pkey, 'md5')
        ctx = SSL.Context(SSL.SSLv23_METHOD)
        ctx.use_privatekey(pkey)
        ctx.use_certificate(cert)
        return ctx



class WSGIHandler(WSGIHandlerMixin, BaseHTTPRequestHandler):
    server_version = 'PasteWSGIServer/' + __version__

    def handle_one_request(self):
        self.raw_requestline = self.rfile.readline()
        if not self.raw_requestline:
            self.close_connection = 1
            return 
        if not self.parse_request():
            return 
        self.wsgi_execute()



    def handle(self):
        try:
            BaseHTTPRequestHandler.handle(self)
        except SocketErrors as exce:
            self.wsgi_connection_drop(exce)



    def address_string(self):
        return ''




class LimitedLengthFile(object):

    def __init__(self, file, length):
        self.file = file
        self.length = length
        self._consumed = 0
        if hasattr(self.file, 'seek'):
            self.seek = self._seek



    def __repr__(self):
        base_repr = repr(self.file)
        return base_repr[:-1] + ' length=%s>' % self.length



    def read(self, length = None):
        left = self.length - self._consumed
        if length is None:
            length = left
        else:
            length = min(length, left)
        if not left:
            return ''
        data = self.file.read(length)
        self._consumed += len(data)
        return data



    def readline(self, *args):
        max_read = self.length - self._consumed
        if len(args):
            max_read = min(args[0], max_read)
        data = self.file.readline(max_read)
        self._consumed += len(data)
        return data



    def readlines(self, hint = None):
        data = self.file.readlines(hint)
        for chunk in data:
            self._consumed += len(chunk)

        return data



    def __iter__(self):
        return self



    def next(self):
        if self.length - self._consumed <= 0:
            raise StopIteration
        return self.readline()



    def _seek(self, place):
        self.file.seek(place)
        self._consumed = place



    def tell(self):
        if hasattr(self.file, 'tell'):
            return self.file.tell()
        else:
            return self._consumed




class ThreadPool(object):
    SHUTDOWN = object()

    def __init__(self, nworkers, name = 'ThreadPool', daemon = False, max_requests = 100, hung_thread_limit = 30, kill_thread_limit = 1800, dying_limit = 300, spawn_if_under = 5, max_zombie_threads_before_die = 0, hung_check_period = 100, logger = None, error_email = None):
        self.nworkers = nworkers
        self.max_requests = max_requests
        self.name = name
        self.queue = Queue.Queue()
        self.workers = []
        self.daemon = daemon
        if logger is None:
            logger = logging.getLogger('paste.httpserver.ThreadPool')
        if isinstance(logger, basestring):
            logger = logging.getLogger(logger)
        self.logger = logger
        self.error_email = error_email
        self._worker_count = count()
        if not killthread:
            kill_thread_limit = 0
            self.logger.info('Cannot use kill_thread_limit as ctypes/killthread is not available')
        self.kill_thread_limit = kill_thread_limit
        self.dying_limit = dying_limit
        self.hung_thread_limit = hung_thread_limit
        self.spawn_if_under = spawn_if_under
        self.max_zombie_threads_before_die = max_zombie_threads_before_die
        self.hung_check_period = hung_check_period
        self.requests_since_last_hung_check = 0
        self.worker_tracker = {}
        self.idle_workers = []
        self.dying_threads = {}
        self._last_added_new_idle_workers = 0
        if not daemon:
            atexit.register(self.shutdown)
        for i in range(self.nworkers):
            self.add_worker_thread(message='Initial worker pool')




    def add_task(self, task):
        self.logger.debug('Added task (%i tasks queued)', self.queue.qsize())
        if self.hung_check_period:
            self.requests_since_last_hung_check += 1
            if self.requests_since_last_hung_check > self.hung_check_period:
                self.requests_since_last_hung_check = 0
                self.kill_hung_threads()
        if not self.idle_workers and self.spawn_if_under:
            busy = 0
            now = time.time()
            self.logger.debug('No idle workers for task; checking if we need to make more workers')
            for worker in self.workers:
                if not hasattr(worker, 'thread_id'):
                    continue
                (time_started, info,) = self.worker_tracker.get(worker.thread_id, (None, None))
                if time_started is not None:
                    if now - time_started < self.hung_thread_limit:
                        busy += 1

            if busy < self.spawn_if_under:
                self.logger.info('No idle tasks, and only %s busy tasks; adding %s more workers', busy, self.spawn_if_under - busy)
                self._last_added_new_idle_workers = time.time()
                for i in range(self.spawn_if_under - busy):
                    self.add_worker_thread(message='Response to lack of idle workers')

            else:
                self.logger.debug('No extra workers needed (%s busy workers)', busy)
        if len(self.workers) > self.nworkers and len(self.idle_workers) > 3 and time.time() - self._last_added_new_idle_workers > self.hung_thread_limit:
            self.logger.info('Culling %s extra workers (%s idle workers present)', len(self.workers) - self.nworkers, len(self.idle_workers))
            self.logger.debug('Idle workers: %s', self.idle_workers)
            for i in range(len(self.workers) - self.nworkers):
                self.queue.put(self.SHUTDOWN)

        self.queue.put(task)



    def track_threads(self):
        result = dict(idle=[], busy=[], hung=[], dying=[], zombie=[])
        now = time.time()
        for worker in self.workers:
            if not hasattr(worker, 'thread_id'):
                continue
            (time_started, info,) = self.worker_tracker.get(worker.thread_id, (None, None))
            if time_started is not None:
                if now - time_started > self.hung_thread_limit:
                    result['hung'].append(worker)
                else:
                    result['busy'].append(worker)
            else:
                result['idle'].append(worker)

        for (thread_id, (time_killed, worker,),) in self.dying_threads.items():
            if not self.thread_exists(thread_id):
                self.logger.info('Killed thread %s no longer around', thread_id)
                try:
                    del self.dying_threads[thread_id]
                except KeyError:
                    pass
                else:
                    continue
            if now - time_killed > self.dying_limit:
                result['zombie'].append(worker)
            else:
                result['dying'].append(worker)

        return result



    def kill_worker(self, thread_id):
        if killthread is None:
            raise RuntimeError('Cannot kill worker; killthread/ctypes not available')
        thread_obj = threading._active.get(thread_id)
        killthread.async_raise(thread_id, SystemExit)
        try:
            del self.worker_tracker[thread_id]
        except KeyError:
            pass
        self.logger.info('Killing thread %s', thread_id)
        if thread_obj in self.workers:
            self.workers.remove(thread_obj)
        self.dying_threads[thread_id] = (time.time(), thread_obj)
        self.add_worker_thread(message='Replacement for killed thread %s' % thread_id)



    def thread_exists(self, thread_id):
        return thread_id in threading._active



    def add_worker_thread(self, *args, **kwargs):
        index = self._worker_count.next()
        worker = threading.Thread(target=self.worker_thread_callback, args=args, kwargs=kwargs, name='worker %d' % index)
        worker.setDaemon(self.daemon)
        worker.start()



    def kill_hung_threads(self):
        if not self.kill_thread_limit:
            return 
        now = time.time()
        max_time = 0
        total_time = 0
        idle_workers = 0
        starting_workers = 0
        working_workers = 0
        killed_workers = 0
        for worker in self.workers:
            if not hasattr(worker, 'thread_id'):
                starting_workers += 1
                continue
            (time_started, info,) = self.worker_tracker.get(worker.thread_id, (None, None))
            if time_started is None:
                idle_workers += 1
                continue
            working_workers += 1
            max_time = max(max_time, now - time_started)
            total_time += now - time_started
            if now - time_started > self.kill_thread_limit:
                self.logger.warning('Thread %s hung (working on task for %i seconds)', worker.thread_id, now - time_started)
                try:
                    import pprint
                    info_desc = pprint.pformat(info)
                except:
                    out = StringIO()
                    traceback.print_exc(file=out)
                    info_desc = 'Error:\n%s' % out.getvalue()
                self.notify_problem('Killing worker thread (id=%(thread_id)s) because it has been \nworking on task for %(time)s seconds (limit is %(limit)s)\nInfo on task:\n%(info)s' % dict(thread_id=worker.thread_id, time=now - time_started, limit=self.kill_thread_limit, info=info_desc))
                self.kill_worker(worker.thread_id)
                killed_workers += 1

        if working_workers:
            ave_time = float(total_time) / working_workers
            ave_time = '%.2fsec' % ave_time
        else:
            ave_time = 'N/A'
        self.logger.info('kill_hung_threads status: %s threads (%s working, %s idle, %s starting) ave time %s, max time %.2fsec, killed %s workers' % (idle_workers + starting_workers + working_workers,
         working_workers,
         idle_workers,
         starting_workers,
         ave_time,
         max_time,
         killed_workers))
        self.check_max_zombies()



    def check_max_zombies(self):
        if not self.max_zombie_threads_before_die:
            return 
        found = []
        now = time.time()
        for (thread_id, (time_killed, worker,),) in self.dying_threads.items():
            if not self.thread_exists(thread_id):
                try:
                    del self.dying_threads[thread_id]
                except KeyError:
                    pass
                else:
                    continue
            if now - time_killed > self.dying_limit:
                found.append(thread_id)

        if found:
            self.logger.info('Found %s zombie threads', found)
        if len(found) > self.max_zombie_threads_before_die:
            self.logger.fatal('Exiting process because %s zombie threads is more than %s limit', len(found), self.max_zombie_threads_before_die)
            self.notify_problem('Exiting process because %(found)s zombie threads (more than limit of %(limit)s)\nBad threads (ids):\n  %(ids)s\n' % dict(found=len(found), limit=self.max_zombie_threads_before_die, ids='\n  '.join(map(str, found))), subject='Process restart (too many zombie threads)')
            self.shutdown(10)
            print 'Shutting down',
            print threading.currentThread()
            raise ServerExit(3)



    def worker_thread_callback(self, message = None):
        thread_obj = threading.currentThread()
        thread_id = thread_obj.thread_id = thread.get_ident()
        self.workers.append(thread_obj)
        self.idle_workers.append(thread_id)
        requests_processed = 0
        add_replacement_worker = False
        self.logger.debug('Started new worker %s: %s', thread_id, message)
        try:
            while True:
                if self.max_requests and self.max_requests < requests_processed:
                    self.logger.debug('Thread %s processed %i requests (limit %s); stopping thread' % (thread_id, requests_processed, self.max_requests))
                    add_replacement_worker = True
                    break
                runnable = self.queue.get()
                if runnable is ThreadPool.SHUTDOWN:
                    self.logger.debug('Worker %s asked to SHUTDOWN', thread_id)
                    break
                try:
                    self.idle_workers.remove(thread_id)
                except ValueError:
                    pass
                self.worker_tracker[thread_id] = [time.time(), None]
                requests_processed += 1
                try:
                    try:
                        runnable()
                    except:
                        print >> sys.stderr, 'Unexpected exception in worker %r' % runnable
                        traceback.print_exc()
                    if thread_id in self.dying_threads:
                        break

                finally:
                    try:
                        del self.worker_tracker[thread_id]
                    except KeyError:
                        pass
                    sys.exc_clear()

                self.idle_workers.append(thread_id)


        finally:
            try:
                del self.worker_tracker[thread_id]
            except KeyError:
                pass
            try:
                self.idle_workers.remove(thread_id)
            except ValueError:
                pass
            try:
                self.workers.remove(thread_obj)
            except ValueError:
                pass
            try:
                del self.dying_threads[thread_id]
            except KeyError:
                pass
            if add_replacement_worker:
                self.add_worker_thread(message='Voluntary replacement for thread %s' % thread_id)




    def shutdown(self, force_quit_timeout = 0):
        self.logger.info('Shutting down threadpool')
        for i in range(len(self.workers)):
            self.queue.put(ThreadPool.SHUTDOWN)

        hung_workers = []
        for worker in self.workers:
            worker.join(0.5)
            if worker.isAlive():
                hung_workers.append(worker)

        zombies = []
        for thread_id in self.dying_threads:
            if self.thread_exists(thread_id):
                zombies.append(thread_id)

        if hung_workers or zombies:
            self.logger.info("%s workers didn't stop properly, and %s zombies", len(hung_workers), len(zombies))
            if hung_workers:
                for worker in hung_workers:
                    self.kill_worker(worker.thread_id)

                self.logger.info('Workers killed forcefully')
            if force_quit_timeout:
                hung = []
                timed_out = False
                need_force_quit = bool(zombies)
                for workers in self.workers:
                    if not timed_out and worker.isAlive():
                        timed_out = True
                        worker.join(force_quit_timeout)
                    if worker.isAlive():
                        print "Worker %s won't die" % worker
                        need_force_quit = True

                if need_force_quit:
                    import atexit
                    for callback in list(atexit._exithandlers):
                        func = getattr(callback[0], 'im_func', None)
                        if not func:
                            continue
                        globs = getattr(func, 'func_globals', {})
                        mod = globs.get('__name__')
                        if mod == 'threading':
                            atexit._exithandlers.remove(callback)

                    atexit._run_exitfuncs()
                    print 'Forcefully exiting process'
                    os._exit(3)
                else:
                    self.logger.info('All workers eventually killed')
        else:
            self.logger.info('All workers stopped')



    def notify_problem(self, msg, subject = None, spawn_thread = True):
        if not self.error_email:
            return 
        if spawn_thread:
            t = threading.Thread(target=self.notify_problem, args=(msg, subject, False))
            t.start()
            return 
        from_address = 'errors@localhost'
        if not subject:
            subject = msg.strip().splitlines()[0]
            subject = subject[:50]
            subject = '[http threadpool] %s' % subject
        headers = ['To: %s' % self.error_email, 'From: %s' % from_address, 'Subject: %s' % subject]
        try:
            system = ' '.join(os.uname())
        except:
            system = '(unknown)'
        body = 'An error has occurred in the paste.httpserver.ThreadPool\nError:\n  %(msg)s\nOccurred at: %(time)s\nPID: %(pid)s\nSystem: %(system)s\nServer .py file: %(file)s\n' % dict(msg=msg, time=time.strftime('%c'), pid=os.getpid(), system=system, file=os.path.abspath(__file__))
        message = '\n'.join(headers) + '\n\n' + body
        import smtplib
        server = smtplib.SMTP('localhost')
        error_emails = [ e.strip() for e in self.error_email.split(',') if e.strip() ]
        server.sendmail(from_address, error_emails, message)
        server.quit()
        print 'email sent to',
        print error_emails,
        print message




class ThreadPoolMixIn(object):

    def __init__(self, nworkers, daemon = False, **threadpool_options):
        self.running = True
        self.thread_pool = ThreadPool(nworkers, ('ThreadPoolMixIn HTTP server on %s:%d' % (self.server_name, self.server_port)), daemon, **threadpool_options)



    def process_request(self, request, client_address):
        request.setblocking(1)
        self.thread_pool.add_task(lambda : self.process_request_in_thread(request, client_address))



    def handle_error(self, request, client_address):
        (exc_class, exc, tb,) = sys.exc_info()
        if exc_class is ServerExit:
            raise 
        return super(ThreadPoolMixIn, self).handle_error(request, client_address)



    def process_request_in_thread(self, request, client_address):
        try:
            self.finish_request(request, client_address)
            self.close_request(request)
        except:
            self.handle_error(request, client_address)
            self.close_request(request)
            exc = sys.exc_info()[1]
            if isinstance(exc, (MemoryError, KeyboardInterrupt)):
                raise 



    def serve_forever(self):
        try:
            while self.running:
                try:
                    self.handle_request()
                except socket.timeout:
                    pass


        finally:
            self.thread_pool.shutdown()




    def server_activate(self):
        self.socket.settimeout(1)



    def server_close(self):
        self.running = False
        self.socket.close()
        self.thread_pool.shutdown(60)




class WSGIServerBase(SecureHTTPServer):

    def __init__(self, wsgi_application, server_address, RequestHandlerClass = None, ssl_context = None, request_queue_size = None):
        SecureHTTPServer.__init__(self, server_address, RequestHandlerClass, ssl_context, request_queue_size=request_queue_size)
        self.wsgi_application = wsgi_application
        self.wsgi_socket_timeout = None



    def get_request(self):
        (conn, info,) = SecureHTTPServer.get_request(self)
        if self.wsgi_socket_timeout:
            conn.settimeout(self.wsgi_socket_timeout)
        return (conn, info)




class WSGIServer(ThreadingMixIn, WSGIServerBase):
    daemon_threads = False


class WSGIThreadPoolServer(ThreadPoolMixIn, WSGIServerBase):

    def __init__(self, wsgi_application, server_address, RequestHandlerClass = None, ssl_context = None, nworkers = 10, daemon_threads = False, threadpool_options = None, request_queue_size = None):
        WSGIServerBase.__init__(self, wsgi_application, server_address, RequestHandlerClass, ssl_context, request_queue_size=request_queue_size)
        if threadpool_options is None:
            threadpool_options = {}
        ThreadPoolMixIn.__init__(self, nworkers, daemon_threads, **threadpool_options)




class ServerExit(SystemExit):
    pass

def serve(application, host = None, port = None, handler = None, ssl_pem = None, ssl_context = None, server_version = None, protocol_version = None, start_loop = True, daemon_threads = None, socket_timeout = None, use_threadpool = None, threadpool_workers = 10, threadpool_options = None, request_queue_size = 5, server_class = None):
    is_ssl = False
    if ssl_pem or ssl_context:
        is_ssl = True
        port = int(port or 4443)
        if not ssl_context:
            if ssl_pem == '*':
                ssl_context = _auto_ssl_context()
            else:
                ssl_context = SSL.Context(SSL.SSLv23_METHOD)
                ssl_context.use_privatekey_file(ssl_pem)
                ssl_context.use_certificate_chain_file(ssl_pem)
    host = host or '127.0.0.1'
    if port is None:
        if ':' in host:
            (host, port,) = host.split(':', 1)
        else:
            port = 8080
    server_address = (host, int(port))
    if not handler:
        handler = WSGIHandler
    if server_version:
        handler.server_version = server_version
        handler.sys_version = None
    if protocol_version:
        handler.protocol_version = protocol_version
    if use_threadpool is None:
        use_threadpool = True
    if converters.asbool(use_threadpool):
        cls = server_class if server_class else WSGIThreadPoolServer
        server = cls(application, server_address, handler, ssl_context, int(threadpool_workers), daemon_threads, threadpool_options=threadpool_options, request_queue_size=request_queue_size)
    else:
        cls = server_class if server_class else WSGIServer
        server = cls(application, server_address, handler, ssl_context, request_queue_size=request_queue_size)
        if daemon_threads:
            server.daemon_threads = daemon_threads
    if socket_timeout:
        server.wsgi_socket_timeout = int(socket_timeout)
    if converters.asbool(start_loop):
        protocol = is_ssl and 'https' or 'http'
        (host, port,) = server.server_address[:2]
        if host == '0.0.0.0':
            print 'serving on 0.0.0.0:%s view at %s://127.0.0.1:%s' % (port, protocol, port)
        else:
            print 'serving on %s://%s:%s' % (protocol, host, port)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
    return server



def server_runner(wsgi_app, global_conf, **kwargs):
    from paste.deploy.converters import asbool
    for name in ['port',
     'socket_timeout',
     'threadpool_workers',
     'threadpool_hung_thread_limit',
     'threadpool_kill_thread_limit',
     'threadpool_dying_limit',
     'threadpool_spawn_if_under',
     'threadpool_max_zombie_threads_before_die',
     'threadpool_hung_check_period',
     'threadpool_max_requests',
     'request_queue_size']:
        if name in kwargs:
            kwargs[name] = int(kwargs[name])

    for name in ['use_threadpool', 'daemon_threads']:
        if name in kwargs:
            kwargs[name] = asbool(kwargs[name])

    threadpool_options = {}
    for (name, value,) in kwargs.items():
        if name.startswith('threadpool_') and name != 'threadpool_workers':
            threadpool_options[name[len('threadpool_'):]] = value
            del kwargs[name]

    if 'error_email' not in threadpool_options and 'error_email' in global_conf:
        threadpool_options['error_email'] = global_conf['error_email']
    kwargs['threadpool_options'] = threadpool_options
    serve(wsgi_app, **kwargs)


server_runner.__doc__ = (serve.__doc__ or '') + '\n\n    You can also set these threadpool options:\n\n    ``threadpool_max_requests``:\n\n        The maximum number of requests a worker thread will process\n        before dying (and replacing itself with a new worker thread).\n        Default 100.\n\n    ``threadpool_hung_thread_limit``:\n\n        The number of seconds a thread can work on a task before it is\n        considered hung (stuck).  Default 30 seconds.\n\n    ``threadpool_kill_thread_limit``:\n\n        The number of seconds a thread can work before you should kill it\n        (assuming it will never finish).  Default 600 seconds (10 minutes).\n\n    ``threadpool_dying_limit``:\n\n        The length of time after killing a thread that it should actually\n        disappear.  If it lives longer than this, it is considered a\n        "zombie".  Note that even in easy situations killing a thread can\n        be very slow.  Default 300 seconds (5 minutes).\n\n    ``threadpool_spawn_if_under``:\n\n        If there are no idle threads and a request comes in, and there are\n        less than this number of *busy* threads, then add workers to the\n        pool.  Busy threads are threads that have taken less than\n        ``threadpool_hung_thread_limit`` seconds so far.  So if you get\n        *lots* of requests but they complete in a reasonable amount of time,\n        the requests will simply queue up (adding more threads probably\n        wouldn\'t speed them up).  But if you have lots of hung threads and\n        one more request comes in, this will add workers to handle it.\n        Default 5.\n\n    ``threadpool_max_zombie_threads_before_die``:\n\n        If there are more zombies than this, just kill the process.  This is\n        only good if you have a monitor that will automatically restart\n        the server.  This can clean up the mess.  Default 0 (disabled).\n\n    `threadpool_hung_check_period``:\n\n        Every X requests, check for hung threads that need to be killed,\n        or for zombie threads that should cause a restart.  Default 100\n        requests.\n\n    ``threadpool_logger``:\n\n        Logging messages will go the logger named here.\n\n    ``threadpool_error_email`` (or global ``error_email`` setting):\n\n        When threads are killed or the process restarted, this email\n        address will be contacted (using an SMTP server on localhost).\n\n'
if __name__ == '__main__':
    from paste.wsgilib import dump_environ
    serve(dump_environ, server_version='Wombles/1.0', protocol_version='HTTP/1.1', port='8888')

