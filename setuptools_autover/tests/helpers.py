from unittest import mock


class MockMixin:
    def mock(self, *args, **kwargs):
        return mock.Mock(*args, **kwargs)

    @property
    def sentinel(self):
        return mock.sentinel

    def patch(self, *args, **kwargs):
        patcher = mock.patch(*args, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()
