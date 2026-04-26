"""Java detector rules (SDLC-056).

Tree-sitter S-expressions for the Java grammar that ships with
``tree-sitter-language-pack``. Patterns target the same families covered
for Go/Rust/Python so cross-language signal stays consistent.
"""

from __future__ import annotations

from typing import Any

from sdlc_assessor.detectors.treesitter.framework import TreeSitterRule

JAVA_SUFFIXES = (".java",)


def _is_empty_block(node: Any) -> bool:
    """Java's catch body is a ``block`` node — empty when no named children."""
    return getattr(node, "named_child_count", 0) == 0


JAVA_RULES: list[TreeSitterRule] = [
    TreeSitterRule(
        subcategory="java_runtime_exec",
        severity="critical",
        category="security_posture",
        statement="`Runtime.getRuntime().exec(...)` invocation — command-injection risk.",
        rationale=(
            "Routing user-controlled strings through Runtime.exec invokes a "
            "shell-like dispatcher; prefer ProcessBuilder with an "
            "argument array."
        ),
        # Two shapes: Runtime.getRuntime().exec(...) and Runtime.exec(...).
        # The outer call's `name` is `exec`; we also assert that somewhere
        # in the call chain there's an identifier `Runtime`.
        query="""
            ((method_invocation
                name: (identifier) @method)
             (#eq? @method "exec")) @match
        """,
        post_filter=lambda node: b"Runtime" in (node.text or b""),
    ),
    TreeSitterRule(
        subcategory="java_class_forname",
        severity="medium",
        category="security_posture",
        statement="`Class.forName(...)` — reflective class load by name.",
        rationale=(
            "Class.forName with a non-constant string allows arbitrary "
            "class loading; restrict to a known allowlist or use a "
            "service-loader pattern."
        ),
        query="""
            ((method_invocation
                object: (identifier) @cls
                name: (identifier) @method)
             (#eq? @cls "Class")
             (#eq? @method "forName")) @match
        """,
    ),
    TreeSitterRule(
        subcategory="java_system_println",
        severity="low",
        category="code_quality_contracts",
        statement="`System.out.println` / `System.err.println` — adopt structured logging.",
        rationale=(
            "Direct stdout/stderr writes bypass any logger config. "
            "java.util.logging, SLF4J, or Log4j 2 are the conventional "
            "choices."
        ),
        query="""
            ((method_invocation
                object: (field_access
                    object: (identifier) @sys
                    field: (identifier) @stream)
                name: (identifier) @method)
             (#eq? @sys "System")
             (#match? @stream "^(out|err)$")
             (#match? @method "^(println|print|printf)$")) @match
        """,
    ),
    TreeSitterRule(
        subcategory="java_print_stack_trace",
        severity="low",
        category="code_quality_contracts",
        statement="`.printStackTrace()` — adopt structured logging instead.",
        rationale=(
            "printStackTrace dumps to stderr without level or context; "
            "log the exception via the project's logger."
        ),
        query="""
            ((method_invocation
                name: (identifier) @method)
             (#eq? @method "printStackTrace")) @match
        """,
    ),
    TreeSitterRule(
        subcategory="java_empty_catch",
        severity="medium",
        category="code_quality_contracts",
        statement="Empty `catch` block detected — error swallowed.",
        rationale=(
            "An empty catch silently absorbs failures; rethrow, log, or "
            "degrade explicitly."
        ),
        query="""
            (catch_clause body: (block) @match)
        """,
        post_filter=_is_empty_block,
    ),
    TreeSitterRule(
        subcategory="java_thread_sleep",
        severity="info",
        category="code_quality_contracts",
        statement="`Thread.sleep(...)` — prefer scheduled-executor or async primitive.",
        rationale=(
            "Thread.sleep blocks the current thread; in service code it "
            "wedges request handlers and is hard to test deterministically."
        ),
        query="""
            ((method_invocation
                object: (identifier) @cls
                name: (identifier) @method)
             (#eq? @cls "Thread")
             (#eq? @method "sleep")) @match
        """,
    ),
    TreeSitterRule(
        subcategory="java_todo_or_fixme",
        severity="info",
        category="documentation_truthfulness",
        statement="`TODO` / `FIXME` / `XXX` left in source.",
        rationale="Open work items should be tracked in an issue tracker, not the code.",
        query="""
            ((line_comment) @c
             (#match? @c "(TODO|FIXME|XXX|HACK)")) @match
        """,
    ),
]


__all__ = ["JAVA_RULES", "JAVA_SUFFIXES"]
