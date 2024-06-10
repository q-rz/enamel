from .header import *

"""Adapted from code_eval (@link https://huggingface.co/spaces/evaluate-metric/code_eval)"""

def get_memory_usage():
    return sys.getsizeof(sys.modules[__name__])

@contextlib.contextmanager
def set_memory_limit(maximum_memory_bytes = None):
    try:
        if maximum_memory_bytes is not None:
            _not_darwin = (not platform.uname().system == "Darwin")
            _rlimit_as = resource.getrlimit(resource.RLIMIT_AS)
            _rlimit_data = resource.getrlimit(resource.RLIMIT_DATA)
            if _not_darwin:
                _rlimit_stack = resource.getrlimit(resource.RLIMIT_STACK)
            memory_limit = int(get_memory_usage() + maximum_memory_bytes)
            resource.setrlimit(resource.RLIMIT_AS, (memory_limit, _rlimit_as[-1]))
            resource.setrlimit(resource.RLIMIT_DATA, (memory_limit, _rlimit_data[-1]))
            if _not_darwin:
                resource.setrlimit(resource.RLIMIT_STACK, (memory_limit, _rlimit_stack[-1]))
        yield
    finally:
        if maximum_memory_bytes is not None:
            resource.setrlimit(resource.RLIMIT_AS, _rlimit_as)
            resource.setrlimit(resource.RLIMIT_DATA, _rlimit_data)
            if _not_darwin:
                resource.setrlimit(resource.RLIMIT_STACK, _rlimit_stack)

class TimeoutException(Exception):
    pass

def timeout_signal_handler(signum, frame):
    raise TimeoutException("Timed out!")

@contextlib.contextmanager
def set_time_limit(seconds):
    import signal
    signal.setitimer(signal.ITIMER_REAL, seconds)
    signal.signal(signal.SIGALRM, timeout_signal_handler)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)

import io

class WriteOnlyStringIO(io.StringIO):
    def read(self, *args, **kwargs):
        raise OSError
    def readline(self, *args, **kwargs):
        raise OSError
    def readlines(self, *args, **kwargs):
        raise OSError
    def readable(self, *args, **kwargs):
        return False

class redirect_stdin(contextlib._RedirectStream):  # type: ignore
    _stream = "stdin"

@contextlib.contextmanager
def swallow_io():
    stream = WriteOnlyStringIO()
    with contextlib.redirect_stdout(stream):
        with contextlib.redirect_stderr(stream):
            with redirect_stdin(stream):
                yield

@contextlib.contextmanager
def chdir(root):
    if root == ".":
        yield
        return
    cwd = os.getcwd()
    os.chdir(root)
    try:
        yield
    except BaseException as exc:
        raise exc
    finally:
        os.chdir(cwd)

@contextlib.contextmanager
def create_tempdir():
    import tempfile
    with tempfile.TemporaryDirectory() as dirname:
        with chdir(dirname):
            yield dirname

@contextlib.contextmanager
def reliability_guard():
    """
    This disables various destructive functions and prevents the generated code
    from interfering with the test (e.g. fork bomb, killing other processes,
    removing filesystem files, etc.)

    WARNING
    This function is NOT a security sandbox. Untrusted code, including, model-
    generated code, should not be blindly executed outside of one. See the
    Codex paper for more information about OpenAI's code sandbox, and proceed
    with caution.
    """

    with create_tempdir():
        with swallow_io():
            try:

                import faulthandler

                faulthandler.disable()

                import builtins, os, shutil, subprocess

                os.environ["OMP_NUM_THREADS"] = "1"

                _keys = dict(
                    builtins = ('exit', 'quit'),
                    os = ('kill', 'system', 'putenv', 'remove', 'removedirs', 'rmdir', 'fchdir', 'setuid', 'fork', 'forkpty', 'killpg', 'rename', 'renames', 'truncate', 'replace', 'unlink', 'fchmod', 'fchown', 'chmod', 'chown', 'chroot', 'lchflags', 'lchmod', 'lchown', 'getcwd', 'chdir'),
                    shutil = ('rmtree', 'move', 'chown'),
                    subprocess = ('Popen',),
                )
                _baks = dict()
                for lib, keys in _keys.items():
                    obj = locals()[lib]
                    _bak = dict()
                    for key in keys:
                        if hasattr(obj, key):
                            _bak[key] = getattr(obj, key)
                    _baks[lib] = _bak

                #__builtins__["help"] = None

                yield
            finally:
                for lib, keys in _keys.items():
                    obj = locals()[lib]
                    for key, val in _baks[lib].items():
                        setattr(obj, key, val)

def unsafe_execute(program: str, exec_globals: dict):
    try:
        gc_bak = gc.isenabled()
        gc.disable()
        with reliability_guard():
            exec(program, exec_globals)
    finally:
        if gc_bak:
            gc.enable()

def unsafe_timed_execute(program: str, exec_globals: dict, maximum_memory_bytes: float, time_limit_seconds: float):
    try:
        gc_bak = gc.isenabled()
        gc.disable()
        with reliability_guard():
            with set_memory_limit(maximum_memory_bytes):
                with set_time_limit(time_limit_seconds):
                    exec(program, exec_globals)
    finally:
        if gc_bak:
            gc.enable()
