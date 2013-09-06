
""" Announcer script by Sarcen """

from twisted.internet import reactor
import platform
import sys

class Announcer(object):
    first_tick = True
    server = None
    time_left = 0
    action = ''
    action_func = None
    action_func_args = None

    abort_message = 'aborted.'
    message = ''
    message_long = ''
    irc_announcement = True

    # Announce frequency, the closer to 0 more frequent it announces
    tick_step_sizes = (60*60, 30*60, 10*60, 5*60, 60, 30, 10, 5)

    def announce_tick(self):
        if self.time_left > 0:

            tick_size = 1
            for i in self.tick_step_sizes:
                if self.time_left > i:
                    tick_size = min(i, self.time_left - i)
                    break

            self.time_left = self.time_left - tick_size
            self.callid = reactor.callLater(tick_size, self.announce_tick)

            announcement = ""

            if ((self.first_tick or (self.time_left+tick_size) >= 10)
                    and not self.reason is None):

                announcement = (self.message_long
                                .format(action=self.action,
                                        time=self.time_left+tick_size,
                                        reason=self.reason))
            else:
                announcement = (self.message
                                .format(action=self.action,
                                        time=self.time_left+tick_size))

            self.show_announcement(announcement)
        else:
            if not self.action_func is None:
                self.action_func(*self.action_func_args)

        self.first_tick = False

    def announce(self):
        self.first_tick = True
        self.announce_tick()

    def show_announcement(self, announcement):
        self.server.send_chat(announcement)

        if self.irc_announcement:
            try:
                self.server.scripts.irc.send(announcement)
            except AttributeError:
                self.irc_announcement = False
            except KeyError:
                self.irc_announcement = False

        print announcement

    def abort(self):
        self.show_announcement(self.abort_message)
        self.callid.cancel()
