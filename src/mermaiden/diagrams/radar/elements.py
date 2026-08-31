from ...core.domain import Entity


class RadarAxis(Entity):
    pass


class RadarCurve(Entity):
    values: tuple[float, ...] = ()
