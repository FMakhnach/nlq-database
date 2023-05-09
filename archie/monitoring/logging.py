import logging

logger = logging.getLogger(__name__)
__indent_level = 0


def log(message: str, level=logging.WARNING):
    indent = '  ' * __indent_level
    logger.log(level, indent + message.replace('\n', '\n' + indent))


def log_function(func):
    def wrapper(*args, **kwargs):
        global __indent_level

        is_member_function = func.__name__ != func.__qualname__
        # Skip first arg (self) for member functions
        args_str = str(args[1:]) if is_member_function else str(args)

        # Log the function parameters
        args_str = args_str + ('' if kwargs is None or len(kwargs) == 0 else ' | ' + str(kwargs))
        log(f"{func.__name__}: {args_str}")

        try:
            __indent_level += 1
            result = func(*args, **kwargs)
            # Log the function result
            log(f"Result: {result}")
            # Return the original result
            return result
        except Exception as e:
            log(f'ERROR: {e}', level=logging.ERROR)
            raise
        finally:
            __indent_level -= 1

    return wrapper


def log_wrap_function_call(func, wrap: str = '==============='):
    def wrapper(*args, **kwargs):
        log(wrap)
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            log(wrap)

    return wrapper
