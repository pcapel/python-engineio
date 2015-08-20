from flask import Flask, render_template

import engineio

async_mode = 'threading'

eio = engineio.Server(async_mode=async_mode)
app = Flask(__name__)
app.wsgi_app = engineio.Middleware(eio, app.wsgi_app)


@app.route('/')
def index():
    return render_template('index.html')


@eio.on('connect')
def connect(sid, environ):
    print("connect ", sid)


@eio.on('message')
def message(sid, data):
    print('message from', sid, data)
    eio.send(sid, 'Thank you for your message!', binary=False)


@eio.on('disconnect')
def disconnect(sid):
    print('disconnect ', sid)


if __name__ == '__main__':
    if async_mode == 'threading':
        # deploy with Werkzeug
        app.run(threaded=True)
    elif async_mode == 'eventlet':
        # deploy with eventlet
        import eventlet
        from eventlet import wsgi
        wsgi.server(eventlet.listen(('', 5000)), app)
    elif async_mode == 'gevent':
        # deploy with gevent
        from gevent import pywsgi
        try:
            from geventwebsocket.handler import WebSocketHandler
            websocket = True
        except ImportError:
            websocket = False
        if websocket:
            pywsgi.WSGIServer(('', 5000), app,
                              handler_class=WebSocketHandler).serve_forever()
        else:
            pywsgi.WSGIServer(('', 5000), app).serve_forever()
    else:
        print('Unknown async_mode: ' + async_mode)
