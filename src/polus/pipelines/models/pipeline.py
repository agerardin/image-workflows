from pydantic import BaseModel


class Plugin(BaseModel):
    """A plugin represents a specific implementation of a algorithm.

    name: the name the plugin should be referred as.
    manifest: the path or url to the plugin manifest.
    """

    name: str
    manifest: str


class Step(BaseModel):
    """A step represents the execution of a plugin.

    params : configuration of a given plugin params
    """

    plugin: Plugin
    params: dict[str, object]


class Pipeline(BaseModel):
    """A pipeline is a set of computation steps."""

    name: str
    steps: list[dict[str, Step]]
