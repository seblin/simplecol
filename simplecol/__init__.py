from .core import FrameBuilder
from .preprocessing import prepare

__all__ = ["columnize", "cprint"]

def columnize(
    values, spacer="  ", width=None, vertical=True, side="left",
    colidx=None, pattern=None, unique=False, sort=False
):
    builder = FrameBuilder(spacer, width, vertical)
    frame = builder.get_frame(
        prepare(values, colidx, pattern, unique, sort)
    )
    frame.align(side)
    return frame

def cprint(*args, **kwargs):
    print(columnize(*args, **kwargs))