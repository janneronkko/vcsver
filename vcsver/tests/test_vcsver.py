import pytest

from .. import vcsver
from .. import errors
from .. import types


@pytest.mark.parametrize(
    ('latest_tag', 'latest_version'),
    (
        ('tag-1.0', '1.0'),
        (None, None),
    ),
)
def test_get_version_from_vcs(
    mocker,
    latest_tag,
    latest_version,
):
    parse_tag_mock = mocker.Mock(
        return_value=latest_version,
    )

    create_version_mock = mocker.Mock(
        return_value=mocker.sentinel.version,
    )

    parse_pkg_info_file_mock = mocker.patch(
        'vcsver.util.parse_pkg_info_file',
        return_value={
            'Version': mocker.sentinel.pkg_info_version,
        },
    )

    version = vcsver.get_version(
        root_version=mocker.sentinel.root_version,
        read_revision_info=lambda: types.RevisionInfo(
            latest_tag=latest_tag,
            distance=0,
            commit=mocker.sentinel.commit,
            dirty=False,
        ),
        parse_tag=parse_tag_mock,
        create_version=create_version_mock,
    )

    assert version == mocker.sentinel.version

    if latest_tag is None:
        assert not parse_tag_mock.called

    else:
        parse_tag_mock.assert_called_once_with(latest_tag)

    create_version_mock.assert_called_once_with(
        types.VersionInfo(
            latest_release=latest_version or mocker.sentinel.root_version,
            distance=0,
            commit=mocker.sentinel.commit,
            dirty=False,
        ),
    )
    assert not parse_pkg_info_file_mock.called


@pytest.mark.parametrize(
    'pkg_info_result',
    (
        {'Version': '1.5.9'},
        FileNotFoundError('pkg-info file not found'),
        PermissionError('no read permission to file'),
    ),
)
def test_get_version_from_pkg_info_file(
    mocker,
    pkg_info_result,
):
    parse_pkg_info_file_mock = mocker.patch(
        'vcsver.util.parse_pkg_info_file',
    )

    expecting_version = not isinstance(pkg_info_result, Exception)
    if expecting_version:
        parse_pkg_info_file_mock.return_value = pkg_info_result

    else:
        parse_pkg_info_file_mock.side_effect = pkg_info_result

    try:
        version = vcsver.get_version(
            root_version=mocker.sentinel.root_version,
            read_revision_info=lambda: None,
            parse_tag=None,
            create_version=None,
        )
        assert version == '1.5.9'
        assert expecting_version

    except errors.RevisionInfoNotFoundError:
        assert not expecting_version

    parse_pkg_info_file_mock.assert_called_once_with('PKG-INFO')
