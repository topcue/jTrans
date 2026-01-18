import sys
import os
import site
import platform
import traceback

sys.path.insert(0, r"C:\Users\user\workspace\IDA-python\jtrans\Lib")
sys.path.insert(0, r"C:\Users\user\workspace\IDA-python\jtrans\libs")
sys.path.insert(0, r"C:\Users\user\workspace\IDA-python\jtrans")
sys.path.insert(0, r"C:\Users\user\workspace\IDA-python\jtrans\Lib\site-packages")

def p(*a):
    print("[IDAPY]", *a)

p("platform:", platform.platform())
p("python version:", sys.version)
p("executable:", sys.executable)
p("prefix:", sys.prefix)
p("base_prefix:", getattr(sys, "base_prefix", None))
p("cwd:", os.getcwd())
p("__file__:", __file__)

p("==== sys.path ====")
for i, x in enumerate(sys.path):
    p(i, x)

try:
    p("site.getsitepackages():", site.getsitepackages())
except Exception:
    p("site.getsitepackages(): <error>")
try:
    p("site.getusersitepackages():", site.getusersitepackages())
except Exception:
    p("site.getusersitepackages(): <error>")

#! Test import
p("==== import test: binaryai ====")
try:
    import binaryai
    p("binaryai imported OK:", binaryai, "from", getattr(binaryai, "__file__", None))
except Exception as e:
    p("binaryai import FAILED:", repr(e))
    traceback.print_exc()

try:
    import ida_pro
    ida_pro.qexit(0)
except Exception:
    pass

# EOF
