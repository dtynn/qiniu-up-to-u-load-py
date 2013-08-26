import os
on_sae = False
if 'SERVER_SOFTWARE' in os.environ:
    on_sae = True

if on_sae:
    import tornado.web
    import tornado.ioloop
    from tornado.httpserver import HTTPServer
else:
    import tornado.wsgi
    import sae

import qiniu.conf
import qiniu.rs
import qiniu.io
#import qiniu.rpc as rpc
#import qiniu.conf as conf

#for test
#import qiniu.httplib_chunk as httplib


class UploadHdl(tornado.web.RequestHandler):
    def get(self):
        self.render('upload.html')
        return


class ResultHdl(tornado.web.RequestHandler):
    def post(self):
        data = self.get_argument('data', 'no data')
        a_key = self.get_argument('access_key', None)
        s_key = self.get_argument('secret_key', None)
        bucket = self.get_argument('bucket', None)
        if data and a_key and s_key and bucket:
            extra = qiniu.io.PutExtra()
            extra.mime_type = "text/plain"
            qiniu.conf.ACCESS_KEY = str(a_key)
            qiniu.conf.SECRET_KEY = str(s_key)
            bucket = str(bucket)
            policy = qiniu.rs.PutPolicy(bucket)
            token = policy.token()

            #for test
            #fields = dict()
            #if extra.params:
            #    for k in extra.params:
            #        fields[k] = str(extra.params[k])
            #
            #if extra.check_crc:
            #    fields["crc32"] = str(extra.crc32)
            #
            #fields["token"] = token
            #
            #files = [
            #    {'filename': 'sae_test.txt', 'data': data, 'mime_type': extra.mime_type},
            #]
            #
            #end
            #cli = rpc.Client(conf.UP_HOST)
            #content_type, mr = cli.encode_multipart_formdata(fields, files)
            #content_length = mr.length()
            #conn = httplib.HTTPConnection(conf.UP_HOST)

            #conn.request('POST', '/', mr, header)
            #resp = conn.getresponse()
            #ret = resp.read()
            #err = True
            #self.write(str(resp.status))

            #cli.set_header("User-Agent", conf.USER_AGENT)
            #if content_type is not None:
            #    cli.set_header("Content-Type", content_type)
            #if content_length is not None:
            #    cli.set_header("Content-Length", content_length)

            #header = cli._header
            #self.write(str(header))
            #conn.request('POST', '/', mr, header)
            #resp = conn.getresponse()

            #self.write(str(resp.read()))
            #self.write(str(resp.status))
            #data = 'test'

            ret, err = qiniu.io.put(token, None, data, extra)
            self.write(str(ret))
            #if not err:
            #    data = 'http://%s.qiniudn.com/%s' % (bucket, ret['key'])
            #else:
            #    data = 'ret:%s;err:%s' % (ret, err)
        self.render('result.html', data=data)
        return


settings = dict(
    debug=True,
    cookie_domain='qiniuuploadpy.sinaapp.com',
    login_url='/',
    template_path='tmpl',
)

urls = [
    ('/', UploadHdl),
    ('/result', ResultHdl),
]


#app = tornado.wsgi.WSGIApplication(urls, **settings)
app = tornado.web.Application(urls, **settings)
server = HTTPServer(app, xheaders=True)
server.bind(50001)
server.start()
tornado.ioloop.IOLoop.instance().start()
#application = sae.create_wsgi_app(app)
