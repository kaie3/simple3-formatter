"""s3fmt — 最小限の公開 API

コア実装を簡潔な公開インターフェースとして再エクスポートします。
"""
from .core import Simple3Formatter

# convenience re-exports
format = Simple3Formatter.format
parse = Simple3Formatter.parse

__all__ = ["Simple3Formatter", "format", "parse"]
