from __future__ import annotations
import asyncio
from .util.ts import merge_seq, merge_plot_maps
from collections import defaultdict
from .stage import Stage
from typing import List, Callable, Optional, Dict, Tuple
from functools import wraps
from .types import *

import typing
if typing.TYPE_CHECKING:
    from .target import Target


def set_pulse(cls):
    cls.pulse = True
    return cls


class ActionMeta(type):
    instances = {}
    targets = defaultdict(str)

    def __new__(cls, name, bases, attr, **kwds):
        return type.__new__(cls, name, bases, attr)

    def __init__(cls, new, bases, attr, offset=False):
        cls.instances: list[Action] = []
        cls.pulse = False
        cls._offset: bool = offset  # the library writer may override the default behavior
        ActionMeta.instances[cls.__name__] = cls

        def add_offset(f: Callable):
            # special case for Action
            if cls.__base__ is object:
                return f
            # handle inheritance: if the base class is offset, then the subclass needs not to
            if not cls._offset and cls.__base__._offset:
                cls._offset = True
                return f
            cls._offset = True

            @wraps(f)
            def ret_func(self, *args, **kwds):
                f(self, *args, **kwds)
                if self.retv is not None:
                    if isinstance(self.retv, tuple):
                        self.retv = self.add_offset(
                            self.retv[0]), *self.retv[1:]
                    else:
                        self.retv = self.add_offset(self.retv)
            return ret_func
        cls.__init__ = add_offset(cls.__init__)

    async def run_preprocess_cls(cls, target: 'Target'):
        await asyncio.gather(*[inst.run_preprocess(target)
                               for inst in target.actions[cls]])

    def to_time_sequencer_cls(cls, target: 'Target'):
        return merge_seq(*[inst.to_time_sequencer(target)
                           for inst in target.actions[cls]])

    def to_plot_cls(cls, target: 'Target', *args, **kwargs):
        return merge_plot_maps(*[inst.to_plot(target, *args, **kwargs)
                                 for inst in target.actions[cls]])

    async def run_postprocess_cls(cls, target: 'Target'):
        await asyncio.gather(*[inst.run_postprocess(target)
                               for inst in target.actions[cls]])

    def cleanup(cls):
        cls.instances: list[Action] = []

    def __str__(cls) -> str:
        return cls.__name__


class Action(metaclass=ActionMeta):
    def __init__(self, signame=None, polarity=False, retv=None, init_state=None, is_temp=False) -> None:
        self.signame = signame
        self.retv = retv
        self.polarity = polarity
        self._offset = Stage.cur  # offset in time marked by Stage
        if init_state is not None:
            self.polarity = init_state
        if not is_temp:
            type(self).instances.append(self)

    def add_offset(self, l: List):
        return [x + self._offset for x in l]

    async def run_preprocess(self, target: 'Target'):
        print(
            f'[Warning] Action {type(target).__name__}.{type(self).__name__} has no preprocess to run.')

    def to_time_sequencer(self, target: 'Target') -> Optional[ts_map]:
        print(
            f'[Warning] Action {type(target).__name__}.{type(self).__name__} has nothing to transform to time sequencer.')

    def to_plot(self, target: 'Target', *args, **kwargs) -> Optional[plot_map]:
        print(
            f'[Warning] Action {type(target).__name__}.{type(self).__name__} has nothing to plot.')

    async def run_postprocess(self, target: 'Target'):
        print(
            f'[Warning] Action {type(target).__name__}.{type(self).__name__} has no postprocess to run.')
