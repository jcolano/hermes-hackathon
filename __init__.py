"""Hermes SMB Growth Agent native plugin."""
from . import schemas, tools

def register(ctx):
    for name, schema in schemas.SCHEMAS.items():
        ctx.register_tool(name=name, toolset="smb_growth", schema=schema, handler=getattr(tools, name))
