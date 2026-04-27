
import re
import unicodedata
from dataclasses import dataclass
import httpx
from app.utils.markdown_parser import MarkdownSection, parse_markdown_sections

@dataclass(frozen=True)
class KnowledgeResult:
    section: str
    content: str
    score: int

class KnowledgeTool:
    def __init__(
        self,
        kb_url: str,
        max_results: int = 2,
        min_score: int = 4,
        timeout_seconds: float = 10.0,
    ) -> None:
        self.kb_url = kb_url
        self.max_results = max_results
        self.min_score = min_score
        self.timeout_seconds = timeout_seconds

    async def search(self, query: str) -> list[KnowledgeResult]:
        markdown = await self._fetch_markdown()
        sections = parse_markdown_sections(markdown)
        ranked = self._rank_sections(query=query, sections=sections)

        return [
            result
            for result in ranked[: self.max_results]
            if result.score >= self.min_score
        ]

    async def _fetch_markdown(self) -> str:
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.get(self.kb_url)
            response.raise_for_status()
            return response.text

    def _rank_sections(
        self,
        query: str,
        sections: list[MarkdownSection],
    ) -> list[KnowledgeResult]:
        query_text = _normalize(query)
        query_tokens = set(_tokenize(query_text))
        results: list[KnowledgeResult] = []

        for item in sections:
            title_text = _normalize(item.section)
            content_text = _normalize(item.content)
            title_tokens = set(_tokenize(title_text))
            content_tokens = set(_tokenize(content_text))
            score = 0
            if title_text and title_text in query_text:
                score += 6
            score += len(query_tokens & title_tokens) * 3
            score += len(query_tokens & content_tokens)
            if score > 0:
                results.append(
                    KnowledgeResult(
                        section=item.section,
                        content=item.content,
                        score=score,
                    )
                )
        return sorted(results, key=lambda result: result.score, reverse=True)

def _normalize(value: str) -> str:
    without_accents = unicodedata.normalize("NFKD", value)
    ascii_text = without_accents.encode("ascii", "ignore").decode("ascii")
    return ascii_text.casefold()

def _tokenize(value: str) -> list[str]:
    tokens = re.findall(r"[a-z0-9_]+", value)
    return [token for token in tokens if len(token) >= 3 and token not in _STOPWORDS]
_STOPWORDS = {
    "com", "das", "dos", "ela", "ele", "entre", "isso", "nao", "para", "pela", "pelo", "por", "que", "sem", "uma",
}