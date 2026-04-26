"""Kotlin detector rules (SDLC-058)."""

from __future__ import annotations

from typing import Any

from sdlc_assessor.detectors.treesitter.framework import TreeSitterRule

KOTLIN_SUFFIXES = (".kt", ".kts")


def _is_empty_catch(node: Any) -> bool:
    """Kotlin's catch_block contains a `statements` child only when non-empty."""
    return not any(c.type == "statements" for c in node.children)


KOTLIN_RULES: list[TreeSitterRule] = [
    TreeSitterRule(
        subcategory="kotlin_not_null_assertion",
        severity="medium",
        category="code_quality_contracts",
        statement="`!!` not-null assertion — runtime NullPointerException risk.",
        rationale=(
            "`!!` converts a recoverable null path into a process-aborting "
            "NPE. Prefer `?.`, `?: throw IllegalStateException(...)`, or "
            "explicit null checks."
        ),
        # The `!!` is a token under postfix_expression; matching the
        # operator directly is the simplest reliable approach.
        query="""
            (postfix_expression
                ("!!") @match)
        """,
    ),
    TreeSitterRule(
        subcategory="kotlin_runtime_exec",
        severity="critical",
        category="security_posture",
        statement="`Runtime.getRuntime().exec(...)` invocation — command-injection risk.",
        rationale=(
            "Routing user-controlled strings through Runtime.exec invokes "
            "a shell-like dispatcher; prefer ProcessBuilder."
        ),
        query="""
            ((call_expression
                (navigation_expression
                    (navigation_suffix
                        (simple_identifier) @method))) @match
             (#eq? @method "exec"))
        """,
        post_filter=lambda node: b"Runtime" in (node.text or b""),
    ),
    TreeSitterRule(
        subcategory="kotlin_println_call",
        severity="low",
        category="code_quality_contracts",
        statement="`println(...)` call — adopt structured logging.",
        rationale=(
            "Direct stdout writes bypass any logger config. SLF4J via "
            "kotlin-logging is the conventional choice for JVM Kotlin."
        ),
        query="""
            ((call_expression
                (simple_identifier) @fn) @match
             (#match? @fn "^(println|print)$"))
        """,
    ),
    TreeSitterRule(
        subcategory="kotlin_todo_call",
        severity="info",
        category="code_quality_contracts",
        statement="`TODO(...)` stdlib call — explicitly unimplemented code path.",
        rationale=(
            "`TODO()` throws NotImplementedError at runtime. Useful "
            "during development; surfacing it as a finding flags incomplete "
            "code that may have shipped."
        ),
        query="""
            ((call_expression
                (simple_identifier) @fn) @match
             (#eq? @fn "TODO"))
        """,
    ),
    TreeSitterRule(
        subcategory="kotlin_empty_catch",
        severity="medium",
        category="code_quality_contracts",
        statement="Empty `catch` block detected — error swallowed.",
        rationale="An empty catch silently absorbs failures; rethrow, log, or degrade explicitly.",
        query="""
            (catch_block) @match
        """,
        post_filter=_is_empty_catch,
    ),
    TreeSitterRule(
        subcategory="kotlin_todo_or_fixme",
        severity="info",
        category="documentation_truthfulness",
        statement="`TODO` / `FIXME` / `XXX` comment left in source.",
        rationale="Open work items belong in an issue tracker, not embedded in code.",
        query="""
            (
              [(line_comment) (multiline_comment)] @c
              (#match? @c "(TODO|FIXME|XXX|HACK)")
            ) @match
        """,
    ),
]


__all__ = ["KOTLIN_RULES", "KOTLIN_SUFFIXES"]
