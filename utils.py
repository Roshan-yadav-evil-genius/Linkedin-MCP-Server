from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.models import MarkdownGenerationResult

def _markdown_from_result(result: MarkdownGenerationResult) -> str:
    if result is None:
        return ""
    raw = getattr(result, "raw_markdown", None)
    if isinstance(raw, str):
        return raw
    if hasattr(result, "model_dump"):
        dumped = result.model_dump()
        if isinstance(dumped.get("raw_markdown"), str):
            return dumped["raw_markdown"]
    return ""


def html_to_markdown(html: str) -> str:
    generator = DefaultMarkdownGenerator()
    result = generator.generate_markdown(html)
    return _markdown_from_result(result)