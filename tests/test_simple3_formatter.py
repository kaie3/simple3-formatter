# tests/test_simple3_formatter.py
import pytest
from simple3_formatter.simple3_formatter import Simple3Formatter as S3F

# テストデータ定義（可読性向上のため定数化）
BASICS = [
    (0, "0.00"),
    (1, "1.00"),
    (12, "12.0"),
    (111, "111"),
    (1111, "1.11K"),
    (11111, "11.1K"),
    (111111, "111K"),
    (0.00123, "1.23m"),
    (0.00000123, "1.23µ"),
    (0.00000000123, "1.23n"),
]

ROUNDING_MODES = [
    (11119, "round", "11.1K"),
    (11119, "floor", "11.1K"),
    (11111, "ceil",  "11.2K"),
    (0.001239, "floor", "1.23m"),
    (0.001231, "ceil",  "1.24m"),
]

PARSE_VALID = [
    ("1.23K", 1230.0),
    ("1.23µ", 1.23e-6),
    ("-1.23K", -1230.0),
    ("9,876.5K", 9876.5 * 1000),
    ("1_234.0K", 1_234.0 * 1000),
]

PARSE_INVALID = ["123", "1.23k", "1.23 X", "abc", "12.3Mm"]


def _assert_format_cases(cases):
    """ヘルパー: 複数のフォーマットケースを検証する"""
    for value, expected in cases:
        assert S3F.format(value) == expected


# 基本フォーマット（3桁＝整数＋小数）
@pytest.mark.parametrize("value,expected", BASICS)
def test_format_basics(value, expected):
    assert S3F.format(value) == expected


# 丸めに伴う単位繰り上げとカンマ区切り
def test_format_grouping_and_carry():
    assert S3F.format(1000) == "1.00K"        # 1000 → 1.00K
    assert S3F.format(999_999) == "1.00M"     # 999.999K → 丸めで 1000K → 1.00M
    assert S3F.format(123_456_789) == "123M"  # 123.456789M → 123M（整数は小数なし）


# 丸めモード
@pytest.mark.parametrize("value,mode,expected", ROUNDING_MODES)
def test_rounding_modes(value, mode, expected):
    assert S3F.format(value, mode=mode) == expected


# 負数
@pytest.mark.parametrize(
    "value,expected",
    [
        (-1, "-1.00"),
        (-12, "-12.0"),
        (-111, "-111"),
        (-1234, "-1.23K"),
        (-0.00000123, "-1.23µ"),
    ],
)
def test_negative_values(value, expected):
    assert S3F.format(value) == expected


# 解析（SI 接頭辞必須、大小区別、区切り入力許容）
@pytest.mark.parametrize("s,expected", PARSE_VALID)
def test_parse_valid_float(s, expected):
    assert S3F.parse(s) == pytest.approx(expected)


# 解析は SI 接頭辞なしを拒否。大小も厳密。
@pytest.mark.parametrize("s", PARSE_INVALID)
def test_parse_invalid_raises(s):
    with pytest.raises(ValueError):
        S3F.parse(s)


# as_str=True のとき、repr がアンダースコア区切りになる内部型を返す
def test_parse_as_str_underscore_repr_int():
    x = S3F.parse("1.23K", as_str=True)  # 1230
    # repr はアンダースコア区切り
    assert repr(x) == "1_230"
    # 数値としても利用可能
    assert int(x) == 1230


def test_parse_as_str_underscore_repr_float():
    y = S3F.parse("1.2345m", as_str=True)  # 0.0012345
    # 小数は Python の '_' 区切りは整数部のみ対象なので repr は 0.0012345 のまま
    assert repr(y) == "0.0012345"
    assert float(y) == pytest.approx(0.0012345)


# 「常に3桁」ルールの確認
def test_three_char_rule_consistency():
    assert S3F.format(9)    == "9.00"
    assert S3F.format(99)   == "99.0"
    assert S3F.format(999)  == "999"
    assert S3F.format(9500) == "9.50K"
