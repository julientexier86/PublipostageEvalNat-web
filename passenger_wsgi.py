import sys, os, traceback, datetime, pathlib
BASE = pathlib.Path(__file__).parent
LOG = BASE / "tmp" / "passenger_boot.log"
try:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"\n[{datetime.datetime.utcnow().isoformat()}Z] Boot start\n")
        f.write(f"sys.executable={sys.executable}\n")
        f.write(f"sys.version={sys.version}\n")
        f.write("PYTHONPATH:\n  " + "\n  ".join(sys.path) + "\n")
    from a2wsgi import ASGIMiddleware
    from app.main import app as asgi_app
    application = ASGIMiddleware(asgi_app)
    with LOG.open("a", encoding="utf-8") as f:
        f.write("Boot OK\n")
except Exception as e:
    with LOG.open("a", encoding="utf-8") as f:
        f.write("Boot ERROR: " + repr(e) + "\n")
        f.write(traceback.format_exc() + "\n")
    def application(environ, start_response):
        start_response('500 Internal Server Error',[('Content-Type','text/plain; charset=utf-8')])
        return [b'App boot error']
