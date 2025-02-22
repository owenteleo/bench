from src.configuration.v1 import Configuration

def test_has_builder():
    assert hasattr(Configuration, "builder")
    assert callable(Configuration.builder)

def test_construct_builder():
    builder = Configuration.builder()
    assert builder is not None
    assert type(builder) == Configuration.Builder

def test_build():
    buidler = Configuration.builder()
    config = buidler.build()
    assert config is not None
    assert type(config) == Configuration
