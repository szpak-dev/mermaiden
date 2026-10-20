from enum import StrEnum
from typing import Annotated

from pydantic import Field

from ...core.characters import Text
from ..domain import MermaidDiagramConfiguration, TextOrUnconfigured


class GanttDisplayMode(StrEnum):
    DEFAULT = ""
    COMPACT = "compact"


class GanttWeekday(StrEnum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class GanttConfiguration(MermaidDiagramConfiguration):
    title_top_margin: Annotated[int, Field(alias="titleTopMargin", ge=0)] = 25
    bar_height: Annotated[int, Field(alias="barHeight", ge=0)] = 20
    bar_gap: Annotated[int, Field(alias="barGap", ge=0)] = 4
    top_padding: Annotated[int, Field(alias="topPadding", ge=0)] = 50
    right_padding: Annotated[int, Field(alias="rightPadding", ge=0)] = 75
    left_padding: Annotated[int, Field(alias="leftPadding", ge=0)] = 75
    grid_line_start_padding: Annotated[int, Field(alias="gridLineStartPadding", ge=0)] = 35
    font_size: Annotated[int, Field(alias="fontSize", ge=0)] = 11
    section_font_size: Annotated[int, Field(alias="sectionFontSize", ge=0)] = 11
    number_section_styles: Annotated[int, Field(alias="numberSectionStyles", gt=0)] = 4
    axis_format: Annotated[str, Field(alias="axisFormat", pattern=Text.pattern, description=Text.description)] = (
        "%Y-%m-%d"
    )
    tick_interval: Annotated[
        TextOrUnconfigured,
        Field(alias="tickInterval", exclude_if=TextOrUnconfigured().excludes),
    ] = Field(default_factory=TextOrUnconfigured)
    top_axis: Annotated[bool, Field(alias="topAxis")] = False
    display_mode: Annotated[GanttDisplayMode, Field(alias="displayMode")] = GanttDisplayMode.DEFAULT
    weekday: Annotated[GanttWeekday, Field(alias="weekday")] = GanttWeekday.SUNDAY
