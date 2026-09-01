import sys

from wireup import create_sync_container, injectable

from mermaiden import Application


@injectable
class CallerService:
    pass


class TestPublicApplicationImport:
    def test_caller_wireup_scan_does_not_adopt_the_public_application(self) -> None:
        container = create_sync_container(injectables=[sys.modules[__name__]], config={})

        assert isinstance(container.get(CallerService), CallerService)
        assert not hasattr(Application, "__wireup_registration__")

    def test_application_create_remains_the_public_composition_boundary(self) -> None:
        assert Application.create().available_diagrams()
