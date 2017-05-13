import datetime


class HumanTimeFormatter():
    """docstring for HumanTimeFormatter"""

    def __init__(self, seconds):
        if type(seconds) is int:
            self.seconds = seconds
        if type(seconds) is float:
            self.seconds = int("%.0f" % seconds)
        if type(seconds) is str:
            self.seconds = int(seconds)
        if type(seconds) is datetime.timedelta:
            calculated = 0
            days = seconds.days
            calculated = calculated + days * 24 * 3600
            calculated = calculated + seconds.seconds
            self.seconds = calculated

    def format(self):
        days, rem = divmod(self.seconds, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, seconds = divmod(rem, 60)
        if seconds < 1: seconds = 1
        locals_ = locals()
        magnitudes_str = ("{n} {magnitude}".format(n=int(locals_[magnitude]), magnitude=magnitude)
                          for magnitude in ("days", "hours", "minutes", "seconds") if locals_[magnitude])
        eta_str = ", ".join(magnitudes_str)
