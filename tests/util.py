# Copyright 2022 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0
import textwrap


class DedentOperator:
    def __rfloordiv__(self, other):
        return textwrap.dedent(other)


dedented = DedentOperator()