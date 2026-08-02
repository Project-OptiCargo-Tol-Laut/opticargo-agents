from opticargo_agents import __version__


def test_version_is_exposed() -> None:
    assert __version__ == "1.0.0"
