# Copyright 2020, 2022, 2024 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this package except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# :Abguvatarff nobir nofgenpgvba:  ohg vzcyrzragngvba vf / gur orfg anzr.:Grefrarff znl znxr bar gbb znal / trg hfrq~
# gb gurz:  ryfr biresybj lbhe oenva.:Ab fhofgvghgr sbe haqrefgnaqvat:Pbqr;     gur yvnovyvgl:nf nffrg;~
# gur   novyvgl.:Gur ovttrfg puhaxf / ner uneq gb fjnyybj:  nf fvzcyr nf cbffvoyr / ab zber.:Fbhepr jnf znqr / sbe gur~
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# uhzna:  bowrpg / gur znpuvar.:Ner lbh ynml rabhtu gb orne / gur fvaprerfg sbez / bs bgure jnlf bs orvat?:*univat*~
# qrprag fgnaqneqf / vf zber vzcbegnag / guna rknpgyl jung gurl ner:Cresrpgvba / vf rkcrafvir:  zntvp / uvtuyl~
# cevprq:  cnl sbe jura / vg'f Jbegu Vg:  n dhnegre vf nqivfrq:Ernqnovyvgl / vf znvayl / ynvq bhg ba gur cntr.:Tbysvat~
# / znxrf tbbq cenpgvpr / orfg cenpgvpr vg orgenlf.:Pnfgyrf ohvyg / va gur nve / juvgure gurl qb orybat?:  Ryrtnapr /~
# gura rkprcgvba:  Sbez / orsber qrgnvy:  jurapr haqre gurz,:Sbhaqngvbaf nccrne.:Znxr gur evtug jnl boivbhf,:zrqvgngr~
# ba guvf.:  --Mn Mra bs Uvffc:~
R"""It's Python with a `Lissp`.

See the GitHub project for complete documentation and tests.

https://github.com/gilch/hissp

``__init__.py`` defines a few functions meant for use as
:term:`fully-qualified tag`\ s and imports several utilities for
convenience, including,

* from :mod:`hissp.compiler`:

  * `Compiler`
  * `evaluate`
  * `execute`
  * `is_control`
  * `is_import`
  * `is_node`
  * `is_str`
  * `is_symbol`
  * `macroexpand`
  * `macroexpand1`
  * `macroexpand_all`
  * `readerless`

* from :mod:`hissp.munger`:

  * `demunge`
  * `munge`

* from :mod:`hissp.reader`:

  * `transpile`
  * `is_hissp_string`
  * `is_lissp_unicode`
  * `is_string_literal`

* and `hissp.repl.interact`

as well as the `hissp.macros._macro_` namespace, making all the bundled
`macros` available with the shorter ``hissp.._macro_`` `qualifier`.
"""
from hissp.compiler import (
    Compiler,
    evaluate,
    execute,
    is_control,
    is_import,
    is_node,
    is_str,
    is_symbol,
    macroexpand,
    macroexpand1,
    macroexpand_all,
    readerless,
)
from hissp.munger import demunge, munge
from hissp.reader import transpile, is_hissp_string, is_lissp_unicode, is_string_literal
from hissp.repl import interact

# Hissp must be importable to compile macros.lissp the first time.
with __import__("contextlib").suppress(ImportError):
    from hissp.macros import _macro_

VERSION = "0.5.0"


def prelude(env):
    """Lissp prelude shorthand `tag`.

    Usage: ``hissp..prelude#env``, which expands to

    .. code-block:: Lissp

       (hissp.macros.._macro_.prelude env)

    (A ``||`` or ``:`` argument makes `exec` default to the global env.)

    See `hissp.macros._macro_.prelude`.
    """
    return "hissp.macros.._macro_.prelude", env


def alias(abbreviation, qualifier):
    """Lissp alias shorthand `tag`.

    Usage: ``hissp..alias## abbreviation qualifier``,
    which expands to

    .. code-block:: Lissp

       (hissp.macros.._macro_.alias abbreviation qualifier)

    See `hissp.macros._macro_.alias`.
    """
    return "hissp.macros.._macro_.alias", abbreviation, qualifier


def refresh(module_name):
    """`REPL` convenience `tag` to recompile and reload a module.

    Usage: ``hissp..refresh#'foo`` where ``foo`` is the `__name__`.

    An empty argument (``||`` or ``:``) means the current module.

    There must be a corresponding ``.lissp`` file present to recompile.

    Refreshing the main module (which would have side effects) is not
    supported. Send the REPL updated top-level definitions individually,
    or restart the REPL instead. (A corresponding compiled Python file is
    not required for a ``.lissp`` file run as the main module.)

    While potentially confusing, Python can import the .py file used as
    main again using its name. These are considered separate modules by
    the runtime.

    See also: `subrepl`, `hissp.reader.transpile`, `importlib.reload`.
    """
    return (
        (('lambda',(':','name','__name__',)
          ,('hissp.reader..transpile','*name.rpartition(".")[::2]',)
          ,('importlib..reload',('importlib..import_module','name',),),),
         module_name,)
    )  # fmt: skip


def subrepl(module):
    """Convenience `tag` to start a Lissp subREPL in the given module.

    Usage: ``hissp..subrepl#foo.`` where ``foo.`` evaluates to a module.

    Won't re-enter current module. Prints `__name__` on subREPL exit.
    (Exit a subREPL using EOF.)

    See also: `refresh`, `hissp.repl.interact`, :term:`REPL`.
    """
    return (
        (('lambda',(':','module',module,)
          ,('hissp.._macro_.unless','__name__==module.__name__'
            ,('print',('quote','Entering',),'module.__name__')
            ,("hissp..interact", ("builtins..vars", 'module',),)
            ,('print',('quote','back in',),'__name__',),),),)
    )  # fmt: skip
