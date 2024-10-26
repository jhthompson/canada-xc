from datetime import timedelta

from django import template

register = template.Library()


@register.filter
def finish_time(duration: timedelta) -> str:
    """Formats timedelta objects (representing a race duration) to a human readable string.

    Args:
        duration (timedelta): the race duration

    Returns:
        str: human readable string
    """  # noqa
    if not duration:
        return "-"

    total_seconds = int(duration.total_seconds())
    total_minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(total_minutes, 60)

    if hours > 0:
        # don't zero pad hours, but do zero pad minutes and seconds
        return f"{int(hours)}:{int(minutes):02}:{int(seconds):02}"
    elif minutes > 0:
        # don't zero pad minutes, but do zero pad seconds
        return f"{int(minutes)}:{int(seconds):02}"
    else:
        # zero pad minutes to two places when there are only seconds (00:ss)
        return f"{int(minutes):02}:{int(seconds):02}"