
from plugins.genode_plugins_base import GenodePlugin
from plugins.example_plugin import ExamplePlugin

PLUGINS = { ExamplePlugin.name(): ExamplePlugin,
            "test": ExamplePlugin}


def get_plugin_names():
    return list(PLUGINS.keys())

def get_plugin(name):
    return PLUGINS[name]()

