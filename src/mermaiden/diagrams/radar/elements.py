from ...core.element import Entity


class RadarAxis(Entity):
    pass


class RadarCurve(Entity):
    values: tuple[float, ...] = ()
