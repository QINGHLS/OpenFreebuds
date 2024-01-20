from openfreebuds.device.huawei.generic.spp_device import GenericHuaweiSppDevice
from openfreebuds.device.huawei.spp_handlers.anc_change import AncChangeDetectionHandler
from openfreebuds.device.huawei.spp_handlers.anc_control import AncSettingHandler
from openfreebuds.device.huawei.spp_handlers.battery import BatteryHandler
from openfreebuds.device.huawei.spp_handlers.config_equalizer import EqualizerConfigHandler
from openfreebuds.device.huawei.spp_handlers.config_sound_quality import ConfigSoundQualityHandler
from openfreebuds.device.huawei.spp_handlers.device_info import DeviceInfoHandler
from openfreebuds.device.huawei.spp_handlers.drop import DropLogsHandler
from openfreebuds.device.huawei.spp_handlers.gesture_double import DoubleTapConfigHandler
from openfreebuds.device.huawei.spp_handlers.gesture_long import LongTapAction
from openfreebuds.device.huawei.spp_handlers.gesture_long_separate import SplitLongTapActionConfigHandler
from openfreebuds.device.huawei.spp_handlers.gesture_power import PowerButtonConfigHandler
from openfreebuds.device.huawei.spp_handlers.gesture_swipe import SwipeActionHandler
from openfreebuds.device.huawei.spp_handlers.tws_auto_pause import TwsAutoPauseHandler
from openfreebuds.device.huawei.spp_handlers.tws_in_ear import TwsInEarHandler
from openfreebuds.device.huawei.spp_handlers.voice_language import VoiceLanguageHandler


class FreeLaceProDevice(GenericHuaweiSppDevice):
    def __init__(self, address):
        super().__init__(address)

        # Add cooldown to prevent device hang
        self.spp_connect_sleep = 2

        self.handlers = [
            # Drop2b03Handler(),
            DeviceInfoHandler(),
            BatteryHandler(),
            AncSettingHandler(w_cancel_lvl=True, w_reply_nowait=True),
            AncChangeDetectionHandler(),
            PowerButtonConfigHandler(),
            LongTapAction(),
        ]


class FreeBuds4iDevice(GenericHuaweiSppDevice):
    """
    HUAWEI FreeBuds 4i
    """
    def __init__(self, address):
        super().__init__(address)
        self.handlers = [
            DropLogsHandler(),
            DeviceInfoHandler(),
            TwsInEarHandler(),
            AncSettingHandler(),
            BatteryHandler(),
            # TouchpadConfigHandler(),
            DoubleTapConfigHandler(),
            SplitLongTapActionConfigHandler(),
            TwsAutoPauseHandler(),
            VoiceLanguageHandler(),
        ]


class FreeBuds5iDevice(GenericHuaweiSppDevice):
    """
    HUAWEI FreeBuds 5i
    """
    def __init__(self, address):
        super().__init__(address)
        self.handlers = [
            # DropLogsHandler(),
            DeviceInfoHandler(),
            TwsInEarHandler(),
            AncSettingHandler(w_cancel_lvl=True),
            BatteryHandler(),
            DoubleTapConfigHandler(),
            SplitLongTapActionConfigHandler(with_right=True),
            SwipeActionHandler(),
            TwsAutoPauseHandler(),
            ConfigSoundQualityHandler(),
            EqualizerConfigHandler(),
            VoiceLanguageHandler(),
        ]


class FreeBudsPro3Device(GenericHuaweiSppDevice):
    """
    HUAWEI FreeBuds Pro 3
    """
    def __init__(self, address):
        super().__init__(address)
        self.spp_fallback_port = 1
        self.handlers = [
            # May work
            DeviceInfoHandler(),
            TwsInEarHandler(),
            AncSettingHandler(w_cancel_lvl=True, w_cancel_dynamic=True, w_voice_boost=True),
            BatteryHandler(),
            ConfigSoundQualityHandler(),
            EqualizerConfigHandler(),
            # Not tested, no research data
            TwsAutoPauseHandler(),
            VoiceLanguageHandler(),
            DoubleTapConfigHandler(),
            SplitLongTapActionConfigHandler(with_right=True),
            SwipeActionHandler(),
        ]


class FreeBudsSEDevice(GenericHuaweiSppDevice):
    def __init__(self, address):
        super().__init__(address)
        self.handlers = [
            DropLogsHandler(),
            DeviceInfoHandler(),
            BatteryHandler(),
            DoubleTapConfigHandler(),
        ]
