from .target import Target
import asyncio
import shlex
import subprocess

class Program(Target):
    """ Target for running external program """

    def __init__(self, args) -> None:
        """ args is the same as the first argument in subprocess.run """
        super().__init__()
        self.args = args


class MonitorProgram(Program):
    """ Target for running external program """

    def __init__(self, args) -> None:
        """ args is the same as the first argument in subprocess.run """
        super().__init__(args)
        self.proc_handle = len(type(self).backgrounds)
        type(self).backgrounds.append(
            asyncio.create_subprocess_exec(
                *shlex.split(args),
                stdout=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE))

    async def wait_until_ready(self):
        tsk = type(self).tasks[self.proc_handle]
        while not tsk.done() and not tsk.cancelled():
            await asyncio.sleep(0.01)
        if tsk.cancelled():
            raise RuntimeError(f"Error in building program for {type(self).__name__}!")
        self.proc = tsk.result()
        print(f'[INFO] Running monitor program at {self.proc} for {type(self).__name__}')

    async def close(self):
        self.proc.kill()
        await self.proc.wait()
        print(f'[INFO] Monitor program {self.proc} for {type(self).__name__} closed!')


def check_python_existence(substr: str):
    proc = subprocess.Popen(shlex.split("wmic process where " + '"name like ' +
                            "'%python%'" + '" get processid,commandline'), stdout=subprocess.PIPE)
    ret = False
    while True:
        l = proc.stdout.readline()
        if substr.encode() in l:
            ret = True
            break
        if not l:
            break
    return ret