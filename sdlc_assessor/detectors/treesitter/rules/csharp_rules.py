"""C# detector rules (SDLC-057)."""

from __future__ import annotations

from typing import Any

from sdlc_assessor.detectors.treesitter.framework import TreeSitterRule

CSHARP_SUFFIXES = (".cs",)


def _is_empty_block(node: Any) -> bool:
    return getattr(node, "named_child_count", 0) == 0


CSHARP_RULES: list[TreeSitterRule] = [
    TreeSitterRule(
        subcategory="csharp_process_start",
        severity="critical",
        category="security_posture",
        statement="`Process.Start(...)` invocation — command-injection risk if argument is user-controlled.",
        rationale=(
            "Process.Start with a string argument routes through the OS "
            "shell on default ProcessStartInfo. Use ProcessStartInfo with "
            "`UseShellExecute=false` and discrete `Arguments`."
        ),
        query="""
            ((invocation_expression
                function: (member_access_expression
                    expression: (identifier) @cls
                    name: (identifier) @method))
             (#eq? @cls "Process")
             (#eq? @method "Start")) @match
        """,
    ),
    TreeSitterRule(
        subcategory="csharp_unsafe_method",
        severity="high",
        category="security_posture",
        statement="`unsafe` modifier on a method — manual pointer arithmetic.",
        rationale=(
            "Code under `unsafe` bypasses the CLR's bounds and type checks; "
            "the cost-of-mistake is high. Each unsafe method needs a "
            "documented invariant."
        ),
        query="""
            ((method_declaration
                (modifier) @mod)
             (#eq? @mod "unsafe")) @match
        """,
    ),
    TreeSitterRule(
        subcategory="csharp_console_writeline",
        severity="low",
        category="code_quality_contracts",
        statement="`Console.WriteLine` / `Console.Error.WriteLine` — adopt structured logging.",
        rationale=(
            "Direct console writes bypass any logger config. ILogger from "
            "Microsoft.Extensions.Logging is the conventional choice."
        ),
        query="""
            ((invocation_expression
                function: (member_access_expression
                    expression: (identifier) @cls
                    name: (identifier) @method))
             (#eq? @cls "Console")
             (#match? @method "^(WriteLine|Write|Error)$")) @match
        """,
    ),
    TreeSitterRule(
        subcategory="csharp_dynamic_type",
        severity="medium",
        category="code_quality_contracts",
        statement="`dynamic` type used — type-checking deferred to runtime.",
        rationale=(
            "`dynamic` defers method/member resolution to runtime; the "
            "compiler can't help with refactors or typos. Prefer "
            "explicit interfaces or generics."
        ),
        query="""
            ((variable_declaration
                type: (identifier) @t)
             (#eq? @t "dynamic")) @match
        """,
    ),
    TreeSitterRule(
        subcategory="csharp_empty_catch",
        severity="medium",
        category="code_quality_contracts",
        statement="Empty `catch` block detected — error swallowed.",
        rationale="An empty catch silently absorbs failures; rethrow, log, or degrade explicitly.",
        query="""
            (catch_clause body: (block) @match)
        """,
        post_filter=_is_empty_block,
    ),
    TreeSitterRule(
        subcategory="csharp_todo_or_fixme",
        severity="info",
        category="documentation_truthfulness",
        statement="`TODO` / `FIXME` / `XXX` left in source.",
        rationale="Open work items belong in an issue tracker, not the code.",
        query="""
            ((comment) @c
             (#match? @c "(TODO|FIXME|XXX|HACK)")) @match
        """,
    ),
]


__all__ = ["CSHARP_RULES", "CSHARP_SUFFIXES"]
