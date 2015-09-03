class AppSettings(object):
    def __init__(self, prefix):
        self.prefix = prefix

    def _setting(self, name, dflt):
        from django.conf import settings
        return getattr(settings, self.prefix + name, dflt)

    @property
    def NUMBER_PER_USER(self):
        """ Invitations number per user """
        return self._setting('NUMBER_PER_USER', 3)

    @property
    def INVITATION_ONLY(self):
        """ Signup is invite only """
        return self._setting('INVITATION_ONLY', False)


app_settings = AppSettings('INVITATIONS_')
