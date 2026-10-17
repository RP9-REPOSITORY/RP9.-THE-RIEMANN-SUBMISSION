from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote


# ============================================================
# MRF / A.P.X LOCAL GENERATOR
# VERSION 1.5.4
# ============================================================
#
# PURPOSE
#   Run locally inside the folder that shall be represented.
#
#   Creates or updates:
#
#       0. A.P.X. <FOLDER NAME>/
#       ├── M.R.F. <FOLDER NAME>.md
#       └── index & Links. <FOLDER NAME>.md
#
# MRF = MACHINE-READABLE FORMAT
#
# PRINCIPLE
#   SOURCE FOLDER
#       ↓
#   MACHINE-READABLE REPRESENTATION
#       ↓
#   LOCAL NAVIGATION
#
# IMPORTANT
#   A.P.X is always excluded from the source scan.
#   The running script is also excluded.
#   Existing M.C.A files are never created, modified or deleted.
#
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

SCRIPT_VERSION = "1.5.4"
MRF_SYSTEM_NAME = "MRF — MACHINE-READABLE FORMAT"

ALLOWED_EXTENSIONS = (
    ".md",
    ".txt",
    ".py",
    ".json",
    ".csv",
    ".log",
    ".yaml",
     ".pdf",
    ".yml",
)

APX_FOLDER_TEMPLATE = "0. A.P.X. {BASE_NAME}"
LOCAL_INDEX_TEMPLATE = "index & Links. {BASE_NAME}.md"
MCA_NAME = "00. M.C.A.md"

# Extra system folder names that shall never be scanned.
# The generated A.P.X folder name is intentionally NOT listed here.
# Only this execution root's own A.P.X folder is excluded from MRF.
# Nested "000. A.P.X" folders remain traversable.
EXCLUDED_FOLDER_NAMES = {
    "00. MASKIN LÄSNING",
    "00. MASKINLÄSNING",
}

# Generated MRF files found below the current root are excluded from
# a new MRF aggregation to prevent redundant machine-readable nesting.
# Other nested A.P.X files remain eligible.
GENERATED_MRF_PREFIXES = (
    "00. M.R.F. ",
    "00.MRF. ",
    "M.R.F. ",
)

# Legacy generated F.R.C folders are excluded if they exist.
EXCLUDED_FOLDER_PREFIXES = (
    "00. MASKINLÄSNING (F.R.C) — ",
)

# Common files that should not become source material.
EXCLUDED_FILE_NAMES = {
    "desktop.ini",
    "00. index & Links.md",
    MCA_NAME,
}

# Optional repository metadata.
REPOSITORY_NAME = "RP9. RH. Z0"

PACKAGE_PURPOSE = (
    "Machine-readable local representation for structured review, "
    "source tracing, cross-document analysis and rapid navigation."
)

PACKAGE_KEYWORDS = [
    "MRF",
    "Machine-Readable Format",
    "A.P.X",
    "local index",
    "source tracing",
    "structured review",
]

SCOPE_STATEMENT = (
    "This MRF contains all includable text-based source material found "
    "inside the selected local root folder at execution time. "
    "A.P.X, hidden folders, explicitly excluded system folders, legacy "
    "generated export folders, the running script and unsupported file "
    "types are not included."
)

PAUSE_AT_END = True


# ============================================================
# ROOT / OUTPUT PATHS
# ============================================================

THIS_SCRIPT = Path(__file__).resolve()
ROOT = THIS_SCRIPT.parent
BASE_NAME = ROOT.name
APX_FOLDER_NAME = APX_FOLDER_TEMPLATE.format(BASE_NAME=BASE_NAME)
LOCAL_INDEX_NAME = LOCAL_INDEX_TEMPLATE.format(BASE_NAME=BASE_NAME)
EXCLUDED_FILE_NAMES.add(LOCAL_INDEX_NAME)

APX_PATH = ROOT / APX_FOLDER_NAME

MRF_NAME = f"M.R.F. {BASE_NAME}.md"
MRF_PATH = APX_PATH / MRF_NAME
LOCAL_INDEX_PATH = APX_PATH / LOCAL_INDEX_NAME
MCA_PATH = APX_PATH / MCA_NAME


# ============================================================
# DATA MODEL
# ============================================================

@dataclass
class SourceRecord:
    sequence: int
    filename: str
    relative_path: str
    extension: str
    size_bytes: int
    modified_local: str
    line_count: int
    word_count: int
    character_count: int
    sha256: str
    anchor: str
    encoding: str
    read_error: str | None = None


# ============================================================
# SORTING / FILTERING
# ============================================================

def natural_sort_key(value: str) -> list[object]:
    return [
        int(part) if part.isdigit() else part.casefold()
        for part in re.split(r"(\d+)", value)
    ]


def is_hidden_name(name: str) -> bool:
    return name.startswith(".")


def is_excluded_directory(path: Path) -> bool:
    name = path.name

    if is_hidden_name(name):
        return True

    # Exclude only the A.P.X belonging to the root currently being generated.
    # Nested folders with the same name remain traversable.
    try:
        if path.resolve() == APX_PATH.resolve():
            return True
    except OSError:
        pass

    if name in EXCLUDED_FOLDER_NAMES:
        return True

    if any(name.startswith(prefix) for prefix in EXCLUDED_FOLDER_PREFIXES):
        return True

    return False


def is_allowed_source_file(path: Path) -> bool:
    if not path.is_file():
        return False

    if path.resolve() == THIS_SCRIPT:
        return False

    if path.name in EXCLUDED_FILE_NAMES:
        return False

    if is_hidden_name(path.name):
        return False

    # MRF-only exclusion:
    # do not merge nested generated MRF documents into a higher-level MRF.
    if (
        path.suffix.casefold() == ".md"
        and any(path.name.startswith(prefix) for prefix in GENERATED_MRF_PREFIXES)
    ):
        return False

    # Exclude this root's own generated A.P.X output.
    try:
        if APX_PATH.resolve() in path.resolve().parents:
            return False
    except OSError:
        pass

    return path.suffix.casefold() in ALLOWED_EXTENSIONS


def collect_source_paths(root: Path) -> list[Path]:
    collected: list[Path] = []

    for dirpath, dirnames, filenames in os.walk(root):
        current_dir = Path(dirpath)

        dirnames[:] = sorted(
            [
                dirname
                for dirname in dirnames
                if not is_excluded_directory(current_dir / dirname)
            ],
            key=natural_sort_key,
        )

        for filename in sorted(filenames, key=natural_sort_key):
            path = current_dir / filename

            if is_allowed_source_file(path):
                collected.append(path)

    return collected


# ============================================================
# READING / ANALYSIS
# ============================================================

def read_text_robust(path: Path) -> tuple[str, str]:
    encodings = (
        "utf-8-sig",
        "utf-8",
        "cp1252",
        "latin-1",
    )

    last_error: Exception | None = None

    for encoding in encodings:
        try:
            return path.read_text(encoding=encoding), encoding
        except UnicodeDecodeError as error:
            last_error = error
        except OSError:
            raise

    raise UnicodeError(
        f"Could not decode file. Last error: {last_error}"
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file_handle:
        for block in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest()


def count_words(text: str) -> int:
    return len(re.findall(r"\S+", text))


def make_anchor(relative_path: str) -> str:
    normalized = relative_path.replace("\\", "/").strip()
    slug = normalized.casefold()

    slug = re.sub(r"\.[a-z0-9]+$", "", slug)
    slug = re.sub(r"[^a-z0-9åäöæøüß]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")

    if not slug:
        slug = "source"

    short_hash = hashlib.sha1(
        normalized.encode("utf-8")
    ).hexdigest()[:10]

    return f"mrf-{slug}-{short_hash}"


def analyze_sources(
    paths: list[Path],
) -> tuple[list[SourceRecord], dict[str, str]]:
    records: list[SourceRecord] = []
    contents: dict[str, str] = {}

    for sequence, path in enumerate(paths, start=1):
        relative_path = path.relative_to(ROOT).as_posix()
        stat = path.stat()

        read_error: str | None = None
        text = ""
        encoding = "unread"

        try:
            text, encoding = read_text_robust(path)
        except Exception as error:
            read_error = f"{type(error).__name__}: {error}"
            text = (
                "MRF READ ERROR\n\n"
                f"Source: {relative_path}\n\n"
                f"Error: {read_error}\n"
            )

        record = SourceRecord(
            sequence=sequence,
            filename=path.name,
            relative_path=relative_path,
            extension=path.suffix.casefold(),
            size_bytes=stat.st_size,
            modified_local=datetime.fromtimestamp(
                stat.st_mtime
            ).astimezone().isoformat(timespec="seconds"),
            line_count=text.count("\n") + (1 if text else 0),
            word_count=count_words(text),
            character_count=len(text),
            sha256=sha256_file(path),
            anchor=make_anchor(relative_path),
            encoding=encoding,
            read_error=read_error,
        )

        records.append(record)
        contents[relative_path] = text

    return records, contents


# ============================================================
# STRUCTURE DATA
# ============================================================

def build_json_tree(records: list[SourceRecord]) -> dict:
    tree: dict = {}

    for record in records:
        parts = Path(record.relative_path).parts
        pointer = tree

        for folder in parts[:-1]:
            pointer = pointer.setdefault(folder, {})

        pointer.setdefault("_files", []).append(parts[-1])

    def sort_tree(node: dict) -> dict:
        sorted_node: dict = {}

        for key in sorted(
            (key for key in node if key != "_files"),
            key=natural_sort_key,
        ):
            sorted_node[key] = sort_tree(node[key])

        if "_files" in node:
            sorted_node["_files"] = sorted(
                node["_files"],
                key=natural_sort_key,
            )

        return sorted_node

    return sort_tree(tree)


def build_ascii_tree(records: list[SourceRecord]) -> list[str]:
    tree = build_json_tree(records)

    def render_node(node: dict, prefix: str = "") -> list[str]:
        lines: list[str] = []

        folder_names = [
            key for key in node.keys() if key != "_files"
        ]
        filenames = node.get("_files", [])

        entries: list[tuple[str, str, dict | None]] = []
        entries.extend(
            ("folder", name, node[name])
            for name in folder_names
        )
        entries.extend(
            ("file", name, None)
            for name in filenames
        )

        for index, (entry_type, name, child) in enumerate(entries):
            is_last = index == len(entries) - 1
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{name}")

            if entry_type == "folder" and child is not None:
                extension = "    " if is_last else "│   "
                lines.extend(
                    render_node(child, prefix + extension)
                )

        return lines

    return [BASE_NAME, ""] + render_node(tree)


# ============================================================
# MARKDOWN HELPERS
# ============================================================

def human_size(size_bytes: int) -> str:
    value = float(size_bytes)

    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.2f} {unit}"
        value /= 1024

    return f"{size_bytes} B"


def markdown_escape_table(value: object) -> str:
    return str(value).replace("|", r"\|").replace("\n", " ")


def safe_code_fence(content: str, language: str) -> str:
    matches = re.findall(r"`+", content)
    longest = max((len(match) for match in matches), default=0)
    fence = "`" * max(3, longest + 1)

    return f"{fence}{language}\n{content.rstrip()}\n{fence}"


def format_source_content(
    record: SourceRecord,
    content: str,
) -> str:
    if record.extension == ".md":
        return content.rstrip()

    language_by_extension = {
        ".txt": "text",
        ".py": "python",
        ".json": "json",
        ".csv": "csv",
        ".log": "text",
        ".yaml": "yaml",
        ".yml": "yaml",
    }

    language = language_by_extension.get(
        record.extension,
        "text",
    )

    return safe_code_fence(content, language)


# ============================================================
# MRF METADATA
# ============================================================

def build_metadata(
    records: list[SourceRecord],
    generated_at: datetime,
) -> dict:
    extension_counts = Counter(
        record.extension for record in records
    )

    error_count = sum(
        record.read_error is not None
        for record in records
    )

    folder_paths = {
        str(Path(record.relative_path).parent)
        for record in records
        if str(Path(record.relative_path).parent) != "."
    }

    return {
        "mrf_system": MRF_SYSTEM_NAME,
        "generator_version": SCRIPT_VERSION,
        "repository": REPOSITORY_NAME or BASE_NAME,
        "package_name": BASE_NAME,
        "package_purpose": PACKAGE_PURPOSE,
        "source_root": str(ROOT),
        "apx_folder": APX_FOLDER_NAME,
        "generated_at_local": (
            generated_at.astimezone().isoformat(
                timespec="seconds"
            )
        ),
        "generated_at_utc": (
            generated_at.astimezone(timezone.utc).isoformat(
                timespec="seconds"
            )
        ),
        "output_mrf": MRF_NAME,
        "output_local_index": LOCAL_INDEX_NAME,
        "source_file_count": len(records),
        "source_folder_count": len(folder_paths),
        "total_source_bytes": sum(
            record.size_bytes for record in records
        ),
        "total_characters": sum(
            record.character_count for record in records
        ),
        "total_words": sum(
            record.word_count for record in records
        ),
        "total_lines": sum(
            record.line_count for record in records
        ),
        "read_error_count": error_count,
        "extensions": dict(
            sorted(extension_counts.items())
        ),
        "keywords": PACKAGE_KEYWORDS,
        "scope": SCOPE_STATEMENT,
    }


# ============================================================
# BUILD MRF DOCUMENT
# ============================================================

def build_mrf_document(
    records: list[SourceRecord],
    contents: dict[str, str],
    metadata: dict,
) -> str:
    lines: list[str] = []

    # --------------------------------------------------------
    # 1. IDENTITY
    # --------------------------------------------------------

    lines.extend(
        [
            f"# M.R.F. {BASE_NAME}",
            "",
            "## MACHINE-READABLE FORMAT",
            "",
            f"> **System:** {MRF_SYSTEM_NAME}",
            ">",
            f"> **Package:** {BASE_NAME}",
            ">",
            f"> **Generator:** v{SCRIPT_VERSION}",
            "",
            "---",
            "",
            "## PACKAGE COMPONENTS",
            "",
            "This generated package consists of two complementary files:",
            "",
            f"- **{MRF_NAME}** — source aggregation, metadata and internal navigation.",
            f"- **{LOCAL_INDEX_NAME}** — navigation to the original files.",
            "",
            "The M.R.F. also provides source-file navigation using the same link "
            "function as the index. The index itself is not included as source material.",
            "",
            "---",
            "",
            "## MRF METADATA",
            "",
            "```json",
            json.dumps(
                metadata,
                indent=4,
                ensure_ascii=False,
            ),
            "```",
            "",
            "---",
            "",
        ]
    )

    # --------------------------------------------------------
    # 2. SCOPE
    # --------------------------------------------------------

    lines.extend(
        [
            "## SCOPE",
            "",
            SCOPE_STATEMENT,
            "",
            "### Inclusion",
            "",
            (
                f"- Included source files: "
                f"**{metadata['source_file_count']}**"
            ),
            (
                f"- Included source folders: "
                f"**{metadata['source_folder_count']}**"
            ),
            (
                f"- Included source size: "
                f"**{human_size(metadata['total_source_bytes'])}**"
            ),
            (
                f"- Approximate word count: "
                f"**{metadata['total_words']}**"
            ),
            (
                f"- Read errors: "
                f"**{metadata['read_error_count']}**"
            ),
            "",
            "### Source authority",
            "",
            (
                "The material below is a sequential aggregation "
                "of the original source files."
            ),
            (
                "Each source remains identified by its complete "
                "relative path, filename, type, modification time "
                "and SHA-256 checksum."
            ),
            "",
            (
                "The MRF is a machine-readable review and transport "
                "representation."
            ),
            "It does not replace the original source files.",
            "",
            "---",
            "",
        ]
    )

    # --------------------------------------------------------
    # 3. MACHINE READING ORIENTATION
    # --------------------------------------------------------

    lines.extend(
        [
            "## MACHINE-READING ORIENTATION",
            "",
            (
                "Use the following hierarchy when locating and "
                "interpreting source material:"
            ),
            "",
            (
                "1. Use the **Document Manifest** to identify "
                "the relevant source."
            ),
            (
                "2. Use the complete relative path as the "
                "source's primary identity."
            ),
            (
                "3. Treat repeated filenames such as README.md "
                "as separate documents."
            ),
            (
                "4. Use the source boundary blocks to distinguish "
                "one source from another."
            ),
            (
                "5. Preserve repository order when reconstructing "
                "sequences or derivations."
            ),
            (
                "6. Attribute statements to the original relative "
                "source path."
            ),
            "",
            "---",
            "",
        ]
    )

    # --------------------------------------------------------
    # 4. JSON STRUCTURE
    # --------------------------------------------------------

    lines.extend(
        [
            "## JSON STRUCTURE",
            "",
            "```json",
            json.dumps(
                build_json_tree(records),
                indent=4,
                ensure_ascii=False,
            ),
            "```",
            "",
            "---",
            "",
        ]
    )

    # --------------------------------------------------------
    # 5. DOCUMENT MANIFEST
    # --------------------------------------------------------

    lines.extend(
        [
            "## 🔗 INTERNAL NAVIGATION — WITHIN THIS M.R.F.",
            "",
            "**SCOPE:**",
            "",
            f"- {MRF_NAME}",
            "",
            "### DOCUMENT MANIFEST",
            "",
            "Both navigation columns open the same source within this M.R.F. "
            "Use Obsidian for heading links or GitHub / HTML for custom anchor links. "
            "HTML links require a renderer that preserves named anchors.",
            "",
            (
                "| Seq. | Source path | Obsidian | GitHub / HTML | Type | Size | Words | "
                "Lines | SHA-256 |"
            ),
            "|---:|:---|:---|:---|:---:|---:|---:|---:|:---|",
        ]
    )

    for record in records:
        lines.append(
            "| "
            f"{record.sequence} | "
            f"{markdown_escape_table(record.relative_path)} | "
            f"[[#SOURCE {record.sequence:04d} — "
            f"{markdown_escape_table(record.filename)}\\|Open]] | "
            f"[Open](#{record.anchor}) | "
            f"{markdown_escape_table(record.extension)} | "
            f"{human_size(record.size_bytes)} | "
            f"{record.word_count} | "
            f"{record.line_count} | "
            f"`{record.sha256[:16]}…` |"
        )

    lines.extend(["", "---", ""])

    # --------------------------------------------------------
    # 6. ASCII TREE
    # --------------------------------------------------------

    lines.extend(
        [
            "## ASCII TREE",
            "",
            "```text",
            *build_ascii_tree(records),
            "```",
            "",
            "---",
            "",
        ]
    )

    # Source-file navigation uses only the sources represented in this M.R.F.
    lines.extend(build_source_file_navigation(records))

    # --------------------------------------------------------
    # 7. MERGED SOURCE CONTENT
    # --------------------------------------------------------

    lines.extend(
        [
            "# MERGED SOURCE CONTENT",
            "",
            (
                "The following sections preserve the deterministic "
                "source order defined in the Document Manifest."
            ),
            "",
            "---",
            "",
        ]
    )

    for record in records:
        content = contents[record.relative_path]
        formatted_content = format_source_content(
            record,
            content,
        )

        lines.extend(
            [
                f'<a id="{record.anchor}" name="{record.anchor}"></a>',
                "",
                "<!-- MRF_SOURCE_BEGIN -->",
                "",
                (
                    f"## SOURCE {record.sequence:04d} — "
                    f"{record.filename}"
                ),
                "",
                (
                    f"**Relative path:** "
                    f"`{record.relative_path}`  "
                ),
                (
                    f"**File type:** "
                    f"`{record.extension}`  "
                ),
                (
                    f"**Encoding:** "
                    f"`{record.encoding}`  "
                ),
                (
                    f"**Size:** "
                    f"`{record.size_bytes}` bytes  "
                ),
                (
                    f"**Modified:** "
                    f"`{record.modified_local}`  "
                ),
                (
                    f"**SHA-256:** "
                    f"`{record.sha256}`  "
                ),
                (
                    f"**Words:** "
                    f"`{record.word_count}`  "
                ),
                (
                    f"**Lines:** "
                    f"`{record.line_count}`"
                ),
                "",
            ]
        )

        if record.read_error:
            lines.extend(
                [
                    (
                        f"**Read status:** ERROR — "
                        f"`{record.read_error}`"
                    ),
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "**Read status:** COMPLETE",
                    "",
                ]
            )

        lines.extend(
            [
                "---",
                "",
                formatted_content,
                "",
                "---",
                "",
                (
                    f"## END SOURCE "
                    f"{record.sequence:04d} — "
                    f"{record.filename}"
                ),
                "",
                "<!-- MRF_SOURCE_END -->",
                "",
                "---",
                "",
            ]
        )

    # --------------------------------------------------------
    # 8. COMPLETION RECORD
    # --------------------------------------------------------

    lines.extend(
        [
            "# MRF COMPLETION RECORD",
            "",
            f"- Package: **{BASE_NAME}**",
            f"- Included sources: **{len(records)}**",
            (
                f"- Read errors: "
                f"**{metadata['read_error_count']}**"
            ),
            (
                f"- Generated: "
                f"**{metadata['generated_at_local']}**"
            ),
            "",
            "The machine-readable aggregation is complete.",
            "",
        ]
    )

    return "\n".join(lines).rstrip() + "\n"


# ============================================================
# LOCAL INDEX
# ============================================================

def is_local_index_excluded(path: Path) -> bool:
    if is_hidden_name(path.name):
        return True

    if path.resolve() == THIS_SCRIPT:
        return True

    if path.is_dir():
        if path.name in {
            "00. MASKIN LÄSNING",
            "00. MASKINLÄSNING",
        }:
            return True

        if any(
            path.name.startswith(prefix)
            for prefix in EXCLUDED_FOLDER_PREFIXES
        ):
            return True

    return False


def collect_local_index_files(root: Path) -> list[Path]:
    collected: list[Path] = []

    for dirpath, dirnames, filenames in os.walk(root):
        current_dir = Path(dirpath)

        dirnames[:] = sorted(
            [
                dirname
                for dirname in dirnames
                if not is_local_index_excluded(current_dir / dirname)
            ],
            key=natural_sort_key,
        )

        for filename in sorted(filenames, key=natural_sort_key):
            path = current_dir / filename

            if is_local_index_excluded(path):
                continue

            if (
                path.is_file()
                and path.suffix.casefold() in ALLOWED_EXTENSIONS
            ):
                collected.append(path)

    return collected


def local_obsidian_link(file_path: Path) -> str:
    """
    Creates an Obsidian wikilink with an explicit alias:

        [[TARGET|LINK NAME]]

    The complete source path is the unique target identity.
    The filename stem is used as the visible link name.
    """
    resolved = file_path.resolve()

    try:
        relative_inside_apx = resolved.relative_to(APX_PATH.resolve())
        relative_target = relative_inside_apx
    except ValueError:
        relative_target = resolved.relative_to(ROOT.resolve())

    # Obsidian Markdown links conventionally omit the .md suffix.
    # Every other supported file type must retain its suffix so that
    # the link resolves to the actual attachment/source file.
    if file_path.suffix.casefold() == ".md":
        target = relative_target.with_suffix("").as_posix()
        link_name = file_path.stem
    else:
        target = relative_target.as_posix()
        link_name = file_path.name

    return f"[[{target}|{link_name}]]"


def build_source_file_navigation(records: list[SourceRecord]) -> list[str]:
    lines = [
        "## 🔗 SOURCE FILE NAVIGATION — ORIGINAL FILES",
        "",
        "**SCOPE:**",
        "",
        f"- {LOCAL_INDEX_NAME}",
        "",
        "The links below open the original files, not their merged content. "
        "Original files must remain available in the Obsidian vault.",
        "",
    ]
    grouped: dict[str, list[SourceRecord]] = {}
    for record in records:
        folder = Path(record.relative_path).parent.as_posix()
        grouped.setdefault(folder, []).append(record)
    for folder in sorted(grouped, key=natural_sort_key):
        label = BASE_NAME if folder == "." else folder
        lines.extend([f"### 📂 {label}", ""])
        for record in grouped[folder]:
            lines.append(f"- {local_obsidian_link(ROOT / record.relative_path)}")
        lines.append("")
    lines.extend(["---", ""])
    return lines


def folder_sort_key(folder_name: str) -> tuple[int, list[object]]:
    if folder_name == APX_FOLDER_NAME:
        return (1, natural_sort_key(folder_name))
    return (0, natural_sort_key(folder_name))


def build_local_index(index_files: list[Path]) -> str:
    lines: list[str] = []

    lines.extend(
        [
            "> [!abstract] **RP9** 🜁 — **index & Links** 🔗",
            ">",
            ">> ",
            ">",
            "> ---",
            "> ",
            f"> ### **📂 — {BASE_NAME}**",
            "> ",
            ">> ###### **🜁 — Links 🔗**",
            ">> ",
            "> ---",
            "> ",
        ]
    )

    if not index_files:
        lines.extend(
            [
                ">> - ###### No supported source files were found.",
                ">",
                "> ---",
                "",
            ]
        )
        return "\n".join(lines).rstrip() + "\n"

    grouped: dict[str, list[Path]] = {}

    for file_path in index_files:
        relative_path = file_path.relative_to(ROOT)
        folder = relative_path.parent.as_posix()
        folder = folder if folder != "." else BASE_NAME
        grouped.setdefault(folder, []).append(file_path)

    ordered_folders = sorted(grouped.keys(), key=folder_sort_key)

    for folder_index, folder in enumerate(ordered_folders):
        lines.append(f"> #### 📂 {folder}")
        lines.append(">")

        files = sorted(
            grouped[folder],
            key=lambda p: natural_sort_key(p.name),
        )

        for file_path in files:
            lines.append(
                f">> - ###### 🔗**{local_obsidian_link(file_path)}**"
            )

        lines.append(">")

        if folder_index != len(ordered_folders) - 1:
            lines.append(">---")
            lines.append(">")

    lines.extend(
        [
            ">---",
            "",
        ]
    )

    return "\n".join(lines).rstrip() + "\n"


# ============================================================
# ATOMIC WRITE
# ============================================================

def atomic_write_text(
    path: Path,
    text: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")

    temporary_path.write_text(
        text,
        encoding="utf-8",
        newline="\n",
    )

    os.replace(temporary_path, path)


# ============================================================
# MAIN PROCESS
# ============================================================

def generate_apx() -> tuple[Path, Path]:
    generated_at = datetime.now().astimezone()

    print("=" * 72)
    print(MRF_SYSTEM_NAME)
    print(f"A.P.X LOCAL GENERATOR v{SCRIPT_VERSION}")
    print("=" * 72)
    print(f"ROOT: {ROOT}")
    print(f"A.P.X: {APX_PATH}")
    print()

    source_paths = collect_source_paths(ROOT)

    if not source_paths:
        raise RuntimeError(
            "No includable source files were found in the root folder."
        )

    print(f"FOUND: {len(source_paths)} source files")
    print()

    records, contents = analyze_sources(source_paths)

    for record in records:
        status = "ERROR" if record.read_error else "ADDING"
        print(
            f"{status}: "
            f"{record.sequence:04d}/{len(records):04d} "
            f"{record.relative_path}"
        )

    metadata = build_metadata(records, generated_at)

    mrf_document = build_mrf_document(
        records,
        contents,
        metadata,
    )

    APX_PATH.mkdir(parents=True, exist_ok=True)

    # 1. Create MRF from the source scan where A.P.X is excluded.
    atomic_write_text(MRF_PATH, mrf_document)

    # 2. Perform a NEW scan for Local Index.
    #    This scan intentionally includes A.P.X, the generated
    #    Markdown files and any existing M.C.A file.
    local_index_files = collect_local_index_files(ROOT)

    # The named local index does not exist yet on a first run.
    # Add its intended path explicitly so the generated index
    # is complete already after one execution.
    if LOCAL_INDEX_PATH not in local_index_files:
        local_index_files.append(LOCAL_INDEX_PATH)

    local_index_files = sorted(
        local_index_files,
        key=lambda path: natural_sort_key(
            path.relative_to(ROOT).as_posix()
        ),
    )

    local_index = build_local_index(local_index_files)
    atomic_write_text(LOCAL_INDEX_PATH, local_index)

    print()
    print("=" * 72)
    print("COMPLETE")
    print(f"MRF:        {MRF_PATH}")
    print(f"LOCAL INDEX:{LOCAL_INDEX_PATH}")
    if MCA_PATH.exists():
        print(f"M.C.A:      PRESERVED — {MCA_PATH}")
    else:
        print("M.C.A:      NOT PRESENT — NOT CREATED")
    print("=" * 72)

    return MRF_PATH, LOCAL_INDEX_PATH


def pause_if_requested() -> None:
    if not PAUSE_AT_END:
        return

    if sys.stdin is not None and sys.stdin.isatty():
        try:
            input("Press ENTER to close...")
        except EOFError:
            pass


if __name__ == "__main__":
    exit_code = 0

    try:
        generate_apx()
    except Exception as error:
        exit_code = 1
        print()
        print("=" * 72)
        print("A.P.X GENERATION FAILED")
        print(f"{type(error).__name__}: {error}")
        print("=" * 72)
    finally:
        pause_if_requested()

    raise SystemExit(exit_code)
