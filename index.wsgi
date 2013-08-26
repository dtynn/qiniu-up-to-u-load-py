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

            ret, err = qiniu.io.put(token, None, data, extra)
            if (type(ret) is dict) and (not err):
                data = 'http://%s.qiniudn.com/%s' % (bucket, ret['key'])
            else:
                data = 'ret:%s;err:%s' % (ret, err)
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


if on_sae:
    app = tornado.wsgi.WSGIApplication(urls, **settings)
    application = sae.create_wsgi_app(app)
else:
    app = tornado.web.Application(urls, **settings)
    server = HTTPServer(app, xheaders=True)
    server.bind(50001)
    server.start()
    tornado.ioloop.IOLoop.instance().start()

