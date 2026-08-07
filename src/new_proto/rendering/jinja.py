from collections.abc import Callable, Mapping
from dataclasses import dataclass

from jinja2 import BaseLoader, Environment, StrictUndefined

from .text import canonical_text


def create_jinja_environment(
    loader: BaseLoader,
    *,
    filters: Mapping[str, Callable[..., object]] | None = None,
) -> Environment:
    environment = Environment(
        loader=loader,
        undefined=StrictUndefined,
        autoescape=False,
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
        newline_sequence="\n",
    )
    if filters is not None:
        environment.filters.update(filters)
    return environment


@dataclass(frozen=True, slots=True)
class JinjaTextRenderer[SourceT]:
    environment: Environment
    template_name: str
    context_name: str = "diagram"

    def render(self, source: SourceT) -> str:
        template = self.environment.get_template(self.template_name)
        rendered = template.render(**{self.context_name: source})
        return canonical_text(rendered)


__all__ = ["JinjaTextRenderer", "create_jinja_environment"]
