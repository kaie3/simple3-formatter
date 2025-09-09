# simple3-formatter

Python で数値を SI 接頭辞付きで「常に 3 桁（整数部＋小数部 = 3）」に整形する小さなユーティリティライブラリです。

特徴
- SI 接頭辞（正: K, M, G, T, P, E / 負: m, µ, n, p, f, a）に対応
- 例: `1.00`, `12.0`, `123` のように常に 3 桁で表示
- `0` は常に `"0.00"`
- 出力はカンマ区切り（例: `1,234.56K`）
- `parse()` は必ず SI 接頭辞が必要（単位なしはエラー）
- `parse(..., as_str=True)` は repr がアンダースコア区切りになる内部数値型を返す

対応 Python バージョン
- Python 3.10 以上

インストール

```bash
uv add git+https://github.com/kaie3/simple3-formatter.git
```

使い方

基本的な使用例:

```python
from s3fmt import Simple3Formatter as sf

# 単純なフォーマット
print(sf.format(1))          # -> '1.00'
print(sf.format(12))         # -> '12.0'
print(sf.format(111))        # -> '111'
print(sf.format(1111))       # -> '1.11K'

# 小数・負数の例
print(sf.format(0.00123))    # -> '1.23m'
print(sf.format(-1234))      # -> '-1.23K'

# カンマ区切り・桁繰り上げの例
print(sf.format(999_999))    # -> '1.00M'  # 丸めで 1000K -> 1.00M
print(sf.format(123_456_789))# -> '123M'   # 整数は小数なし

# 丸めモードの指定（'round'（既定）, 'floor', 'ceil'）
print(sf.format(11111, mode='round'))  # -> '11.1K'
print(sf.format(11111, mode='ceil'))   # -> '11.2K'

# parse: SI 接頭辞つき文字列を数値に変換
print(sf.parse('1.23K'))    # -> 1230.0
print(sf.parse('1.23µ'))    # -> 1.23e-6

# parse(..., as_str=True): repr がアンダースコア区切りになる内部型を返す
x = sf.parse('1.23K', as_str=True)    # 内部は _UnderscoreInt（repr -> '1_230'）
print(repr(x))                         # -> '1_230'
print(int(x))                          # -> 1230

y = sf.parse('1.2345m', as_str=True)  # 内部は _UnderscoreFloat
print(repr(y))                         # -> '0.0012345'
print(float(y))                        # -> 0.0012345
```

API（概要）
- Simple3Formatter.format(value: float, mode: str = 'round') -> str
  - value を SI 接頭辞つきの文字列に整形します。mode は 'round' / 'floor' / 'ceil'。
- Simple3Formatter.parse(value_str: str, *, as_str: bool = False) -> float | internal
  - SI 接頭辞付き文字列を数値に変換します。単位は必須です。

開発

推奨インポート名は `s3fmt` です。

ローカルで pytest を実行する場合:

```bash
uv run --with pytest -m pytest -q
```

ライセンス

MIT

