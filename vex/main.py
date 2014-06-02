"""Main command-line entry-point and any code tightly coupled to it.
"""
import sys
import os
from vex import args
from vex import config
from vex.run import get_ve_base, get_command, make_env, run


def _barf(message):
    """Standard way of reporting an error and bailing.
    """
    sys.stdout.write("Error: " + message + '\n')
    sys.exit(1)


def main():
    """The main command-line entry point.
    """
    # Get options, complain if any unknown stuff crept in
    arg_parser = args.make_arg_parser()
    options, unknown = arg_parser.parse_known_args(sys.argv[1:])
    if unknown:
        arg_parser.print_help()
        return _barf("unknown args: {0!r}".format(unknown))

    vexrc = config.read_vexrc(options.config, environ)
    ve_base = get_ve_base(vexrc)
    if not options.path and not ve_base:
        return _barf(
            "could not figure out a virtualenvs directory. "
            "make sure $HOME is set, or $WORKON_HOME,"
            " or set virtualenvs=something in your .vexrc")
    if not os.path.exists(ve_base):
        return _barf("virtualenvs directory {0!r} not found.".format(ve_base))

    # Find a virtualenv path
    ve_path = options.path
    ve_name = options.virtualenv
    if not ve_path:
        if not ve_name:
            ve_name = options.rest.pop(0) if options.rest else None
        if not ve_name:
            _barf("could not find a virtualenv name in the command line.")
            arg_parser.print_help()
            return 1
        ve_path = os.path.join(ve_base, ve_name)
    assert ve_path
    assert isinstance(ve_path, str)
    ve_path = os.path.abspath(ve_path)
    if not ve_name:
        ve_name = os.path.basename(os.path.normpath(ve_path))
    if not os.path.exists(ve_path):
        return _barf("virtualenv not found at {0!r}.".format(ve_path))
    options.path = ve_path
    options.virtualenv = ve_name

    command = get_command(options, vexrc)
    if not command:
        return _barf("no command")
    env = make_env(os.environ, vexrc['env'], options)
    returncode = run(command, env=env, cwd=options.cwd)
    if returncode is None:
        return _barf("command not found: {0!r}".format(command[0]))
    sys.exit(returncode)
