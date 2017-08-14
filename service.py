import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), "resources", "lib"))

import xbmc
import xbmcaddon

from player import PlayerMonitor


__id__ = 'service.bgmusic'
__addon__ = xbmcaddon.Addon(__id__)

TICK_TIME = 10  # seconds


if __name__ == '__main__':
    monitor = xbmc.Monitor()
    player_monitor = PlayerMonitor()
    player_monitor.attach(__addon__)

    while not monitor.abortRequested():
        player_monitor.tick()

        if monitor.waitForAbort(TICK_TIME):
            break