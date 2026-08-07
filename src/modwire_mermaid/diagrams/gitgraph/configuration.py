from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GitGraphNodeLabel:
    width: float = 75
    height: float = 100
    x: float = -25
    y: float = 0

    def to_mermaid(self) -> dict[str, float]:
        return {"width": self.width, "height": self.height, "x": self.x, "y": self.y}


@dataclass(frozen=True, slots=True)
class GitGraphDiagramConfiguration:
    title_top_margin: int = 25
    diagram_padding: float = 8
    node_label: GitGraphNodeLabel = GitGraphNodeLabel()
    main_branch_name: str = "main"
    main_branch_order: float = 0
    show_commit_label: bool = True
    show_branches: bool = True
    rotate_commit_label: bool = True
    parallel_commits: bool = False
    arrow_marker_absolute: bool = False

    def to_mermaid(self) -> dict[str, object]:
        return {
            "titleTopMargin": self.title_top_margin,
            "diagramPadding": self.diagram_padding,
            "nodeLabel": self.node_label.to_mermaid(),
            "mainBranchName": self.main_branch_name,
            "mainBranchOrder": self.main_branch_order,
            "showCommitLabel": self.show_commit_label,
            "showBranches": self.show_branches,
            "rotateCommitLabel": self.rotate_commit_label,
            "parallelCommits": self.parallel_commits,
            "arrowMarkerAbsolute": self.arrow_marker_absolute,
        }
