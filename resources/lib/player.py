import datetime

import xbmc


class PlayerMonitor(xbmc.Player):
    def __init__(self, *args, **kwargs):
        self.addon = None

        # Statemachine
        self.wait_for_play = False
        self.is_idle = False
        self.last_stopped = datetime.datetime.now()

        super(PlayerMonitor, self).__init__(*args, **kwargs)

    def attach(self, addon):
        self.addon = addon

    @property
    def playlist(self):
        return self.addon.getSetting('playlist')

    @property
    def favorite(self):
        return xbmc.getInfoLabel('Skin.String(Startup.Favourites.Path)')

    @property
    def threshold(self):
        return int(float(self.addon.getSetting('threshold')))

    @property
    def always_active(self):
        return self.addon.getSetting('always_active') == 'true'

    @property
    def start_hr(self):
        return int(self.addon.getSetting('start_hr'))

    @property
    def start_min(self):
        return int(self.addon.getSetting('start_min'))

    @property
    def stop_hr(self):
        return int(self.addon.getSetting('stop_hr'))

    @property
    def stop_min(self):
        return int(self.addon.getSetting('stop_min'))

    @property
    def should_play(self):
        if self.always_active:
            return True
        
        time_of_day = datetime.datetime.now().time()

        if time_of_day > datetime.time(self.start_hr, self.start_min):
            return time_of_day < datetime.time(self.stop_hr, self.stop_min)

        return False

    def tick(self):
        if self.wait_for_play:
            if self.wait_for_play == 1:
                xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Input.Down","id":1}')
                xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Input.Select","id":2}')
                self.wait_for_play = 2
            elif self.wait_for_play == 2:
                xbmc.executebuiltin("PlayerControl(RandomOn)")
                xbmc.executebuiltin("PlayerControl(RepeatAll)")
                xbmc.executebuiltin("PlayerControl(Next)")
                self.wait_for_play = False

        if self.check_conditions():
            self.is_idle = True

            self.trigger()


    def trigger(self):
        if self.favorite:
            xbmc.executebuiltin(self.favorite)
            self.wait_for_play = 1

        else:
            self.play(self.playlist)

            
    def check_conditions(self):
        curr_time = datetime.datetime.now()
        current_idle = divmod(int(xbmc.getGlobalIdleTime()), 60)[0]
        threshold = self.threshold

        # Have we been idle long enough?
        if current_idle < threshold:
            xbmc.log('BGMusic: check_conditions:F {} < {}'.format(current_idle, threshold))
            return False

        # Are we already playing something?
        if self.isPlaying():
            xbmc.log('BGMusic: check_conditions:F isPlaying')
            return False

        # Has it been long enough since something stopped playing?
        time_since_stop = curr_time - self.last_stopped
        if time_since_stop < datetime.timedelta(minutes=threshold):
            xbmc.log('BGMusic: check_conditions:F time_since_stop {} < minutes={} threshold'.format(time_since_stop, threshold))
            return False

        # Are we supposed to be playing at this time
        return self.should_play

    def onPlayBackStarted(self):
        if self.is_idle:
            xbmc.log('BGMusic: User started playback')
            self.is_idle = False

    def onPlayBackStopped(self):
        self.last_stopped = datetime.datetime.now()

        if self.is_idle:
            xbmc.log('BGMusic: User stopped playback')
            self.is_idle = False

    def onPlayBackEnded(self):
        if not self.idling:
            self.last_stopped = datetime.datetime.now()

    def onQueueNextItem(self):
        # TODO: Do we even need this?
        xbmc.log('BGMusic: ::onQueueNextItem::')
