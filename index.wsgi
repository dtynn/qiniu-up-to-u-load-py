import tornado.wsgi
import tornado.web
#import tornado.ioloop
#from tornado.httpserver import HTTPServer
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
            qiniu.conf.ACCESS_KEY = str(a_key)
            qiniu.conf.SECRET_KEY = str(s_key)
            bucket = str(bucket)
            policy = qiniu.rs.PutPolicy(bucket)
            token = policy.token()
            ret, err = qiniu.io.put(token, None, data)
            data = 'http://%s.qiniudn.com/%s' % (bucket, ret['key'])
        self.render('result.html', data=data)
        return


settings = dict(
    cookie_domain='qiniuuploadpy.sinaapp.com',
    login_url='/',
    template_path='tmpl',
)

urls = [
    ('/', UploadHdl),
    ('/result', ResultHdl),
]


app = tornado.wsgi.WSGIApplication(urls, **settings)
#app = tornado.web.Application(urls, **settings)
#server = HTTPServer(app, xheaders=True)
#server.bind(50001)
#server.start()
#tornado.ioloop.IOLoop.instance().start()
