from dataclasses import dataclass
@dataclass(frozen= True)
class MarkdownParser:
    section: str
    content: str
def parse_markdown_section(markdown: str) -> list[MarkdownSection]:
    sections: list[MarkdownSection] = []
    current_title: str | None = None
    current_lines: list[str] = []
    def flush_current() -> None:
        nonlocal current_title, current_lines
        if current_title is None:
            return
        content= "\n".join(current_lines).strip()
        if content:
            sections.append(MarkdownSection(section=current_title, content=content)) 
    for line in markdown.splitlines():
        if line.startswith("## "):
            flush_current()
            current_title = line.removeprefix("## ").strip()
            current_lines = []
            continue
        if current_title is not None:
            current_lines.append(line)
    flush_current()
    return sections