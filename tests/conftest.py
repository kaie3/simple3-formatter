import os
import sys


# インストールせずローカル実行できるよう、`src/` を sys.path に追加
_ROOT = os.path.dirname(os.path.dirname(__file__))
_SRC = os.path.join(_ROOT, "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
