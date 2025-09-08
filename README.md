# simple3-formatter

Python で数値を **SI 接頭辞付きで常に 3 桁（整数＋小数 = 3）** に整形するライブラリです。  
また、厳密なパース機能も備えており、`repr` で **アンダースコア区切り**を表示する特殊数値型を返すこともできます。  

---

## 特徴
- SI 接頭辞に対応  
  - 正の接頭辞: `K, M, G, T, P, E`  
  - 負の接頭辞: `m (10^-3), µ (10^-6), n, p, f, a`  
- 常に「整数部＋小数部＝3 桁」に調整  
  - 例: `1.00`, `12.0`, `123`  
- `0` は `"0.00"` 固定  
- `format()` はカンマ区切りで出力（例: `1,234.56K`）  
- `parse()` は **必ず SI 接頭辞が必要**（単位なしはエラー）  
- `parse(..., as_str=True)` の場合、Python 風にアンダースコア区切りで `repr` を表示する数値型を返す  

---

## インストール
```bash
git clone https://github.com/yourname/simple3-formatter.git
cd simple3-formatter
pip install .
```
## 使用例
```python
from simple3_formatter import Simple3Formatter

# フォーマット
print(Simple3Formatter.format(1111))        # 1.11K
print(Simple3Formatter.format(123456789))   # 123M
print(Simple3Formatter.format(0.00000123))  # 1.23µ

# パース（数値を返す）
print(Simple3Formatter.parse("1.23K"))      # 1230.0

# パース（アンダースコア区切りの repr を持つ特殊数値型を返す）
x = Simple3Formatter.parse("1.23K", as_str=True)
print(x)        # 1230
print(repr(x))  # 1_230
```
テスト
```python
pytest -q
```

