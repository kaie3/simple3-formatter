"""s3fmt のコア実装。

フォーマッタおよびパースの正準実装を提供します。公開 API は
`Simple3Formatter` の static メソッドで構成され、モジュールレベルの
ヘルパー `format` と `parse` は `s3fmt.__init__` から再エクスポートされます。
"""

import math
from typing import Tuple, Union


class _UnderscoreInt(int):
    """repr() がアンダースコア区切りになる内部用の int。"""

    def __repr__(self) -> str:
        return f"{int(self):_}"


class _UnderscoreFloat(float):
    """末尾の 0 を削った短い表現を返す内部用の float。"""

    def __repr__(self) -> str:
        s = f"{float(self):_.10f}".rstrip("0").rstrip(".")
        return s


class Simple3Formatter:
    """SI 接頭辞付きで合計「3 桁」表示を行うフォーマッタ。

    公開メソッド（すべて static）:
      - format(value: float, mode: str = 'round') -> str
      - parse(value_str: str, *, as_str: bool = False) -> float | internal
    """

    UNITS_POS = ["", "K", "M", "G", "T", "P", "E"]
    UNITS_NEG = ["", "m", "µ", "n", "p", "f", "a"]

    # 単位 -> 10 の指数
    UNIT_TO_EXP = {u: i * 3 for i, u in enumerate(UNITS_POS)}
    UNIT_TO_EXP.update({u: -i * 3 for i, u in enumerate(UNITS_NEG)})

    @staticmethod
    def _unit_from_exp3(exp3: int) -> Tuple[int, str]:
        """3 の倍数指数を単位に変換し、対応範囲にクランプする。"""
        if exp3 >= 0:
            idx = min(exp3, len(Simple3Formatter.UNITS_POS) - 1)
            return idx, Simple3Formatter.UNITS_POS[idx]
        lower = -(len(Simple3Formatter.UNITS_NEG) - 1)
        exp3 = max(exp3, lower)
        return exp3, Simple3Formatter.UNITS_NEG[-exp3]

    @staticmethod
    def _digits_for_three_total(scaled_abs: float) -> int:
        """合計 3 桁にするために必要な小数桁数を返す。"""
        if scaled_abs <= 0:
            return 2
        int_digits = int(math.floor(math.log10(scaled_abs))) + 1
        return max(3 - int_digits, 0)

    @staticmethod
    def format(value: float, mode: str = "round") -> str:
        """値を「3 桁」ルールに従って SI 接頭辞付き文字列に整形する。"""
        if mode not in ("round", "floor", "ceil"):
            raise ValueError("mode must be 'round', 'floor', or 'ceil'")

        if value == 0:
            return "0.00"

        abs_val = abs(value)
        if abs_val < 1e-300:
            return "0.00"

        exp3_guess = int(math.floor(math.log10(abs_val) / 3))
        exp3, unit = Simple3Formatter._unit_from_exp3(exp3_guess)

        scaled = value / (10 ** (3 * exp3))
        frac_digits = Simple3Formatter._digits_for_three_total(abs(scaled))

        def _apply_rounding(v: float, digits: int, m: str) -> float:
            factor = 10**digits
            if m == "round":
                return round(v, digits)
            if m == "floor":
                return math.floor(v * factor) / factor
            return math.ceil(v * factor) / factor

        scaled = _apply_rounding(scaled, frac_digits, mode)

        # Carry up if rounding hit 1000
        if abs(scaled) >= 1000:
            exp3, unit = Simple3Formatter._unit_from_exp3(exp3 + 1)
            scaled /= 1000
            frac_digits = Simple3Formatter._digits_for_three_total(abs(scaled))

        if frac_digits == 0:
            return f"{int(round(scaled)):,}{unit}"
        return f"{scaled:,.{frac_digits}f}{unit}"

    @staticmethod
    def parse(
        value_str: str, *, as_str: bool = False
    ) -> Union[float, _UnderscoreInt, _UnderscoreFloat]:
        """SI接尾辞付き文字列を数値に変換します。
        SI単位が必要です。
        as_str=Trueの場合、アンダースコアでグループ化されたrepr形式の内部型を返します。
        """
        s = value_str.strip()
        # 長い単位名（文字数の大きいもの）から優先して評価
        for unit in sorted(Simple3Formatter.UNIT_TO_EXP.keys(), key=len, reverse=True):
            if unit and s.endswith(unit):
                num_str = s[: -len(unit)].replace(",", "").replace("_", "")
                try:
                    num = float(num_str)
                except ValueError:
                    raise ValueError(f"数値部分が不正です: {num_str!r}")
                val = num * (10 ** Simple3Formatter.UNIT_TO_EXP[unit])
                return Simple3Formatter._wrap(val) if as_str else val
        raise ValueError(f"SI接頭辞が必須です: {value_str!r}")

    @staticmethod
    def _wrap(val: float) -> Union[_UnderscoreInt, _UnderscoreFloat]:
        if float(val).is_integer():
            return _UnderscoreInt(int(val))
        return _UnderscoreFloat(val)
