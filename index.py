import os
on_sae = False
if 'SERVER_SOFTWARE' in os.environ or 'APP_NAME' in os.environ or 'APP_VERSION' in os.environ:
    on_sae = True

if on_sae:
    import tornado.wsgi
    import sae
    os.environ['disable_fetchurl'] = True
    SAE_DOMAIN = 'qiniuuploadpy.sinaapp.com'
else:
    import tornado.web
    import tornado.ioloop
    from tornado.httpserver import HTTPServer
    SAE_DOMAIN = 'test.com'

import qiniu.conf
import qiniu.rs
import qiniu.io

import base64
import json
import urllib

PORT = 50001


class Upload2Hdl(tornado.web.RequestHandler):
    def get(self):
        self.render('upload2.html')
        return


class Result2Hdl(tornado.web.RequestHandler):
    def post(self):
        data = self.get_argument('data', None)
        a_key = self.get_argument('access_key', None)
        s_key = self.get_argument('secret_key', None)
        bucket = self.get_argument('bucket', None)
        if data and a_key and s_key and bucket:
            extra = qiniu.io.PutExtra()
            extra.mime_type = "text/html"
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

        data = data or 'no data'
        self.render('result2.html', data=data)
        return


class UploadHdl(tornado.web.RequestHandler):
    def get(self):
        page_data = dict()
        page_data['token'] = self.get_cookie('token', '')
        self.render('upload.html', **page_data)
        return


class TokenHdl(tornado.web.RequestHandler):
    def get(self):
        page_data = dict()
        page_data['current_token'] = self.get_cookie('token', '')
        page_data['current_bucket'] = self.get_cookie('bucket', '')
        self.render('token.html', **page_data)
        return

    def post(self):
        bucket = self.get_argument('bucket', None)
        a_key = self.get_argument('access_key', None)
        s_key = self.get_argument('secret_key', None)
        valid = bucket and a_key and s_key
        if valid:
            qiniu.conf.ACCESS_KEY = str(a_key)
            qiniu.conf.SECRET_KEY = str(s_key)
            bucket = str(bucket)
            policy = qiniu.rs.PutPolicy(bucket)
            policy.returnUrl = 'http://%s/result' % (SAE_DOMAIN,) \
                if on_sae else 'http://%s:%d/result' % (SAE_DOMAIN, PORT)
            token = policy.token()
            self.set_cookie('token', token)
        self.redirect('/upload')
        return


class ResultHdl(tornado.web.RequestHandler):
    def get(self):
        self.post()
        return

    def post(self):
        ret_str = self.get_argument('upload_ret', '')
        err_code = self.get_argument('code', '')
        err_msg = self.get_argument('error', '')

        url = False
        if ret_str:
            try:
                ret = json.loads(base64.b64decode(ret_str))
                url = True
                detail = 'http://%s.qiniudn.com/%s' % (ret['bucket'], ret['key'])
            except Exception as e:
                print e
                detail = 'invalid upload return'
        elif err_code and err_msg:
            detail = 'Err Code:%s|Err Msg:%s' % (err_code, urllib.unquote(err_msg))

        page_data = dict()
        page_data['url'] = url
        page_data['detail'] = detail

        self.render('result.html', **page_data)
        return


settings = dict(
    debug=True,
    cookie_domain=SAE_DOMAIN,
    login_url='/',
    template_path='tmpl',
)

urls = [
    ('/upload', UploadHdl),
    ('/result', ResultHdl),
    ('/token', TokenHdl),
    ('/upload2', Upload2Hdl),
    ('/result2', Result2Hdl),
]


if on_sae:
    app = tornado.wsgi.WSGIApplication(urls, **settings)
    application = sae.create_wsgi_app(app)
else:
    app = tornado.web.Application(urls, **settings)
    server = HTTPServer(app, xheaders=True)
    server.bind(PORT)
    server.start()
    tornado.ioloop.IOLoop.instance().start()