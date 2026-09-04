from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field

from ...core.domain import Container, Entity, ValueModel


class TaskStatus(StrEnum):
    PLANNED = "planned"
    ACTIVE = "active"
    DONE = "done"


class DurationUnit(StrEnum):
    MILLISECONDS = "milliseconds"
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"


class AutomaticStart(ValueModel):
    kind: Literal["automatic"] = "automatic"


class DateStart(ValueModel):
    kind: Literal["date"] = "date"
    date: Annotated[str, Field(min_length=1)]


class DependencyStart(ValueModel):
    kind: Literal["dependencies"] = "dependencies"
    task_ids: Annotated[tuple[Annotated[str, Field(min_length=1)], ...], Field(min_length=1)]


GanttStart = Annotated[AutomaticStart | DateStart | DependencyStart, Field(discriminator="kind")]


class DurationFinish(ValueModel):
    kind: Literal["duration"] = "duration"
    amount: Annotated[float, Field(ge=0)]
    unit: DurationUnit = DurationUnit.DAYS


class EndDateFinish(ValueModel):
    kind: Literal["end_date"] = "end_date"
    date: Annotated[str, Field(min_length=1)]


class UntilFinish(ValueModel):
    kind: Literal["until"] = "until"
    date: Annotated[str, Field(min_length=1)]


GanttFinish = Annotated[DurationFinish | EndDateFinish | UntilFinish, Field(discriminator="kind")]


class Task(Entity):
    status: TaskStatus = TaskStatus.PLANNED
    critical: bool = False
    start: GanttStart
    finish: GanttFinish


class Milestone(Entity):
    status: TaskStatus = TaskStatus.PLANNED
    critical: bool = False
    start: GanttStart
    finish: GanttFinish


class Marker(Entity):
    date: str = ""


class Section(Container):
    pass
