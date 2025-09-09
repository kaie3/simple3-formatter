# simple3_formatter.py
import math
from typing import Tuple, Union


class _UnderscoreInt(int):
    """repr時にアンダースコア区切りで表示される内部用 int"""

    def __repr__(self) -> str:
        return f"{int(self):_}"


class _UnderscoreFloat(float):
    """repr時にアンダースコア区切りで表示される内部用 float"""

    def __repr__(self) -> str:
        s = f"{float(self):_.10f}".rstrip("0").rstrip(".")
        return s


class Simple3Formatter:
    """
    数値を SI 接頭辞付きで「整数部+小数部=常に3桁」に整形するフォーマッタ。

    主要メソッド:
      - format(value, mode): 3桁表示 + SI 接頭辞。整数は小数部なし。0 は "0.00"。
      - parse(text, as_str=False): SI 接頭辞付き文字列のみ受理し数値に変換。

    対応接頭辞:
      正: ""(10^0), K, M, G, T, P, E
      負: ""(10^0), m(10^-3), µ(10^-6), n, p, f, a
    """

    UNITS_POS = ["", "K", "M", "G", "T", "P", "E"]
    UNITS_NEG = ["", "m", "µ", "n", "p", "f", "a"]

    # unit -> 10の指数
    UNIT_TO_EXP = {u: i * 3 for i, u in enumerate(UNITS_POS)}
    UNIT_TO_EXP.update({u: -i * 3 for i, u in enumerate(UNITS_NEG)})

    @staticmethod
    def _unit_from_exp3(exp3: int) -> Tuple[int, str]:
        """3の倍数指数 exp3 をユニットに変換しつつ範囲内にクランプ

        Args:
            exp3 (int): 3刻みの指数

        Returns:
            Tuple[int, str]: 正規化された exp3 と対応する単位文字列
        """
        if exp3 >= 0:
            exp3 = min(exp3, len(Simple3Formatter.UNITS_POS) - 1)
            return exp3, Simple3Formatter.UNITS_POS[exp3]
        else:
            lower = -(len(Simple3Formatter.UNITS_NEG) - 1)
            exp3 = max(exp3, lower)
            return exp3, Simple3Formatter.UNITS_NEG[-exp3]

    @staticmethod
    def _digits_for_three_total(scaled_abs: float) -> int:
        """合計3桁にするための小数桁数を返す

        Args:
            scaled_abs (float): 正のスケール済み絶対値

        Returns:
            int: 必要な小数桁数
        """
        # scaled_abs が 0 以下になる可能性に備えるガード
        if scaled_abs <= 0:
            return 2
        int_digits = int(math.floor(math.log10(scaled_abs))) + 1
        return max(3 - int_digits, 0)

    @staticmethod
    def format(value: float, mode: str = "round") -> str:
        """数値を SI 接頭辞付きでフォーマットする。

        Args:
            value (float): フォーマット対象の数値
            mode (str): 丸めモード。'round'（既定）, 'floor', 'ceil'

        Returns:
            str: フォーマット済み文字列
        """
        if value == 0:
            return "0.00"
        if mode not in ("round", "floor", "ceil"):
            raise ValueError("mode must be 'round', 'floor', or 'ceil'")

        abs_val = abs(value)
        # abs_val が極端に小さい場合の guard
        if abs_val < 1e-300:
            # 過度に小さい値は 0.00 と同等扱い
            return "0.00"

        exp3_guess = int(math.floor(math.log10(abs_val) / 3))
        exp3, unit = Simple3Formatter._unit_from_exp3(exp3_guess)

        scaled = value / (10 ** (3 * exp3))
        frac_digits = Simple3Formatter._digits_for_three_total(abs(scaled))
        factor = 10**frac_digits

        if mode == "round":
            scaled = round(scaled, frac_digits)
        elif mode == "floor":
            scaled = math.floor(scaled * factor) / factor
        else:  # "ceil"
            scaled = math.ceil(scaled * factor) / factor

        # 丸めで 1000 到達したら単位を 1 段繰り上げ
        if abs(scaled) >= 1000:
            exp3_next = exp3 + 1
            exp3, unit = Simple3Formatter._unit_from_exp3(exp3_next)
            scaled /= 1000
            frac_digits = Simple3Formatter._digits_for_three_total(abs(scaled))

        # 出力: frac_digits に基づいて小数の有無を判定しカンマ区切りを適用
        if frac_digits == 0:
            return f"{int(round(scaled)):,}{unit}"
        else:
            # scaled が負の場合でもフォーマットされる
            return f"{scaled:,.{frac_digits}f}{unit}"

    @staticmethod
    def parse(
        value_str: str, *, as_str: bool = False
    ) -> Union[float, _UnderscoreInt, _UnderscoreFloat]:
        """SI接頭辞付き文字列を数値に変換する。

        Args:
            value_str (str): 解析する文字列（単位必須、大小区別）
            as_str (bool): True の場合、内部表示用の型を返す

        Returns:
            float | _UnderscoreInt | _UnderscoreFloat: 解析結果

        Raises:
            ValueError: 単位が無い、または数値部分が不正な場合
        """
        s = value_str.strip()
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
        """整数は _UnderscoreInt、小数は _UnderscoreFloat で返す（内部用）"""
        if float(val).is_integer():
            return _UnderscoreInt(int(val))
        return _UnderscoreFloat(val)
