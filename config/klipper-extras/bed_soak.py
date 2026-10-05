# the pi's python evaluates annotations eagerly, so forward references need this
from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from configfile import ConfigWrapper
    from extras.heaters import Heater


class BedSoak:
    """Publishes bed heater power drift, so TEMPERATURE_WAIT can block on it."""

    SAMPLE_INTERVAL = 1.0
    # reported until the window fills, so a wait cannot pass on a short trace
    UNSETTLED = 999.0
    # only TEMPERATURE_WAIT reads the sensor, so a gap means a new wait began
    WAIT_GAP = 5.0

    # bound at ready, where the heater object exists
    heater: Heater

    def __init__(self, config: ConfigWrapper) -> None:
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]
        self.heater_name: str = config.get("heater", "heater_bed")
        # pid ripple swings power several points sample to sample
        self.window: int = config.getint("window", 40, minval=10)
        # unread here: the option exists for WAIT_BED_SOAK to read the bar from
        self.settled_drift: float = config.getfloat("settled_drift", 2.0, above=0.0)
        # releases the wait when the power never reads steady
        self.max_soak: float = config.getfloat("max_soak", 600.0, above=0.0)
        self.samples: deque[float] = deque(maxlen=self.window)
        self.last_target = 0.0
        self.soak_seconds = 0
        self.gave_up = False
        self.asked_at = 0.0
        self.waiting_since = 0.0
        self.reactor = self.printer.get_reactor()
        self.gcode = self.printer.lookup_object("gcode")
        heaters = self.printer.load_object(config, "heaters")
        heaters.register_sensor(config, self)
        self.printer.register_event_handler("klippy:ready", self._handle_ready)

    def get_temp(self, eventtime: float) -> tuple[float, float]:
        """TEMPERATURE_WAIT polls this by name while it blocks."""
        if eventtime - self.asked_at > self.WAIT_GAP:
            self.waiting_since = eventtime
            self.gave_up = False
        self.asked_at = eventtime
        # bounds the wait even if the bed is switched off while it blocks
        if eventtime - self.waiting_since > self.max_soak and not self.gave_up:
            self.gave_up = True
            self.gcode.respond_info(
                f"{self.name}: no steady power after "
                f"{self.max_soak:.0f}s, releasing the wait"
            )
        return self._drift(), 0.0

    def stats(self, eventtime: float) -> tuple[bool, str]:
        """The statistics module collects this by name into klippy.log."""
        return False, f"{self.name}: drift={self._drift():.2f}"

    def get_status(self, eventtime: float) -> dict[str, float]:
        """Moonraker subscribes to this by name."""
        return {
            "temperature": round(self._drift(), 2),
            "soak_seconds": self.soak_seconds,
        }

    def _handle_ready(self) -> None:
        self.heater = self.printer.lookup_object(self.heater_name)
        self.reactor.register_timer(self._sample, self.reactor.NOW)

    def _sample(self, eventtime: float) -> float:
        status = self.heater.get_status(eventtime)
        target = status["target"]
        if not target or target != self.last_target:
            self.last_target = target
            self.soak_seconds = 0
            self.samples.clear()
        elif self.soak_seconds or status["temperature"] >= target:
            # power saturates flat on the way up, which reads as settled
            self.samples.append(status["power"] * 100.0)
            self.soak_seconds += 1
        return eventtime + self.SAMPLE_INTERVAL

    def _drift(self) -> float:
        if self.gave_up:
            return 0.0
        if len(self.samples) < self.window:
            return self.UNSETTLED
        return self._power_drift(list(self.samples))

    @staticmethod
    def _power_drift(powers: list[float]) -> float:
        """How fast heater power is still changing, in percent per minute."""
        count = len(powers)
        # one sample per second makes the index a second, so the slope is %/s
        mean_index = (count - 1) / 2.0
        mean_power = sum(powers) / count
        covariance = sum(
            (index - mean_index) * (power - mean_power)
            for index, power in enumerate(powers)
        )
        variance = sum((index - mean_index) ** 2 for index in range(count))
        return abs(covariance / variance) * 60.0


# klipper calls this by name to build the object for a [bed_soak] section
# https://www.klipper3d.org/Code_Overview.html#adding-a-host-module
def load_config(config: ConfigWrapper) -> BedSoak:
    return BedSoak(config)
