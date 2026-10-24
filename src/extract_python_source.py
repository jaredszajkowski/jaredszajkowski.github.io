import ast
import re

from pathlib import Path
from typing import Optional


def extract_python_source(
    source_path: Path,
    name: Optional[str] = None,
    section: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    include_banner: bool = False,
) -> str:
    """
    Return a verbatim slice of a Python source file.

    This exists so that posts which walk through a source file can quote it
    directly instead of keeping a pasted copy in `index_temp.md`. A pasted copy
    goes stale silently; a slice taken at notebook execution time cannot.

    Exactly one addressing mode must be supplied:

    `name`
        A top-level function or class. Located with `ast`, so it is immune to
        reformatting and reindentation. If no live definition matches, the file
        is searched for a commented-out `# def <name>(` block, which is returned
        with its comment markers intact.
    `section`
        The body beneath a banner comment of the form::

            #######################################
            ## <section>
            #######################################

        running up to the next such banner. Set `include_banner` to keep the
        banner itself at the top of the returned slice.
    `start` / `end`
        The first line containing `start` through the first subsequent line
        containing `end`, inclusive. Pass `start` alone to slice to end of file.

    Parameters
    ----------
    source_path : Path
        The Python file to read.
    name : str, optional
        Top-level function or class name to extract.
    section : str, optional
        Banner comment heading to extract.
    start : str, optional
        Substring identifying the first line of the slice.
    end : str, optional
        Substring identifying the last line of the slice.
    include_banner : bool, optional
        With `section`, retain the banner comment above the extracted body
        (default: False).

    Returns
    -------
    str
        The extracted source, with surrounding blank lines removed and no
        trailing newline.

    Raises
    ------
    ValueError
        If not exactly one addressing mode is supplied.
    LookupError
        If the requested target is not found. This is deliberate: renaming a
        task in the source should fail the notebook run loudly rather than
        leave a stale code block in the published post.
    """

    modes = [m for m in (name, section, start) if m is not None]
    if len(modes) != 1:
        raise ValueError("Supply exactly one of 'name', 'section', or 'start'.")
    if end is not None and start is None:
        raise ValueError("'end' is only valid together with 'start'.")

    source_path = Path(source_path)
    text = source_path.read_text()
    lines = text.splitlines()

    if name is not None:
        block = _extract_by_name(text, lines, name, source_path)
    elif section is not None:
        block = _extract_by_section(lines, section, source_path, include_banner)
    else:
        block = _extract_by_markers(lines, start, end, source_path)

    while block and not block[0].strip():
        block.pop(0)
    while block and not block[-1].strip():
        block.pop()

    return "\n".join(block)


def _extract_by_name(text, lines, name, source_path):
    """Locate a top-level def/class via ast, falling back to a commented-out block."""
    tree = ast.parse(text)
    wanted = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)

    for node in tree.body:
        if isinstance(node, wanted) and node.name == name:
            first = node.lineno
            for decorator in node.decorator_list:
                first = min(first, decorator.lineno)
            return lines[first - 1 : node.end_lineno]

    # No live definition; look for a commented-out one.
    pattern = re.compile(rf"^\s*#\s*(?:async\s+)?(?:def|class)\s+{re.escape(name)}\b")
    for i, line in enumerate(lines):
        if pattern.match(line):
            block = [line]
            for following in lines[i + 1 :]:
                if following.lstrip().startswith("#") or not following.strip():
                    block.append(following)
                else:
                    break
            return block

    raise LookupError(f"No top-level '{name}' found in {source_path}")


def _extract_by_section(lines, section, source_path, include_banner):
    """Slice the body beneath a `## <section>` banner, up to the next banner."""
    banner = re.compile(r"^#{5,}\s*$")
    heading = f"## {section}"

    for i, line in enumerate(lines):
        if line.strip() != heading:
            continue
        if i == 0 or not banner.match(lines[i - 1]):
            continue
        # Skip the heading and its closing banner rule.
        body_start = (
            i + 2 if i + 1 < len(lines) and banner.match(lines[i + 1]) else i + 1
        )
        slice_start = i - 1 if include_banner else body_start
        for j in range(body_start, len(lines)):
            if banner.match(lines[j]):
                return lines[slice_start:j]
        return lines[slice_start:]

    raise LookupError(f"No '{heading}' banner found in {source_path}")


def _extract_by_markers(lines, start, end, source_path):
    """Slice from the first line containing `start` through the first containing `end`."""
    for i, line in enumerate(lines):
        if start in line:
            if end is None:
                return lines[i:]
            for j in range(i, len(lines)):
                if end in lines[j]:
                    return lines[i : j + 1]
            raise LookupError(
                f"Found start marker {start!r} but no end marker {end!r} in {source_path}"
            )

    raise LookupError(f"No line containing {start!r} in {source_path}")
