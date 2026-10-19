from typing import Annotated

from pydantic import Field

from ...core.characters import Text
from ..domain import MermaidConfigurationModel, MermaidDiagramConfiguration


class GitGraphNodeLabel(MermaidConfigurationModel):
    width: Annotated[float, Field(alias="width")] = 75
    height: Annotated[float, Field(alias="height")] = 100
    x: Annotated[float, Field(alias="x")] = -25
    y: Annotated[float, Field(alias="y")] = 0


class GitGraphDiagramConfiguration(MermaidDiagramConfiguration):
    title_top_margin: Annotated[int, Field(alias="titleTopMargin", ge=0)] = 25
    diagram_padding: Annotated[float, Field(alias="diagramPadding")] = 8
    node_label: Annotated[GitGraphNodeLabel, Field(alias="nodeLabel")] = GitGraphNodeLabel()
    main_branch_name: Annotated[
        str, Field(alias="mainBranchName", pattern=Text.pattern, description=Text.description)
    ] = "main"
    main_branch_order: Annotated[float, Field(alias="mainBranchOrder")] = 0
    show_commit_label: Annotated[bool, Field(alias="showCommitLabel")] = True
    show_branches: Annotated[bool, Field(alias="showBranches")] = True
    rotate_commit_label: Annotated[bool, Field(alias="rotateCommitLabel")] = True
    parallel_commits: Annotated[bool, Field(alias="parallelCommits")] = False
    arrow_marker_absolute: Annotated[bool, Field(alias="arrowMarkerAbsolute")] = False
