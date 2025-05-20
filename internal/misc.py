from pathlib import Path
from typing import get_type_hints


def ensure_path(func):
    """Converts any `str | Path` arguments to `Path`. This is overkill and I'm being rabbit holed lol"""

    def wrapper(*args, **kwargs):
        args = list(args)
        for parameter_index, (parameter_name, parameter_type) in enumerate(get_type_hints(func).items()):
            if parameter_type != (str | Path):
                continue
            if parameter_name == "return":
                continue

            # This logic assumes that the args are always going to be in declaration order
            # Which I guess isn't guaranteed?
            # But dict keys are guaranteed to be in declaration order since like Python 10 or something, so it's FINE
            # (probably)
            if parameter_index < len(args):
                args[parameter_index] = Path(args[parameter_index])
            else:
                kwargs[parameter_name] = Path(kwargs[parameter_name])

        result = func(*args, **kwargs)
        # Add functionality after the original function call
        return result

    return wrapper
