[build-system]
requires = [
  "setuptools",
  "vcsver @ file://${vcsver_wheel_path}",
]
build-backend = "setuptools.build_meta"

% if vcsver_enabled:
[tool.vcsver]
source = "git"
% endif
