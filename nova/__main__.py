import argparse

from .server import serve

p = argparse.ArgumentParser(prog="nova", description="Run Nova OS locally.")
p.add_argument("--port", type=int, default=None)
p.add_argument("--host", default="127.0.0.1")
a = p.parse_args()
serve(a.host, a.port)
