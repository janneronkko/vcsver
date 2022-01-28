import pytest

from .. import setuptools
from .. import types


@pytest.mark.parametrize(
    ('vcsver', 'expected_version'),
    (
        (None, None),
        (True, '1.2.3'),
        ({}, '1.2.3'),
        ({'root_version': '1.0'}, '1.2.3'),
        ({'parse_tag': 'plain'}, '1.2.3'),
        ({'create_version': 'pep440.post_with_dev'}, '1.2.3'),
    ),
)
def test_vcsver(
    mocker,
    vcsver,
    expected_version,
):
    revision_info_reader_mock = mocker.Mock()
    revision_info_reader_mock.return_value.return_value = types.RevisionInfo(
        latest_tag='1.2.3',
        distance=0,
        commit='abcdef',
        dirty=False,
    )

    get_revision_info_reader_mock = mocker.patch(
        'vcsver.config._get_revision_info_reader',
        revision_info_reader_mock,
    )

    dist_mock = mocker.Mock(name='Dist')
    dist_mock.vcsver = vcsver
    dist_mock.metadata.version = None

    setuptools.vcsver(
        dist_mock,
        'vcsver',
        vcsver,
    )

    assert dist_mock.metadata.version == expected_version

    if vcsver is None:
        assert not get_revision_info_reader_mock.called
        return

    get_revision_info_reader_mock.assert_called_once_with(
        vcsver
        if isinstance(vcsver, dict)
        else {}
    )
