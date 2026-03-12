#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
import time
import signal
import sys

class HeadlessWiFiSimulator(gr.top_block):
    def __init__(self, use_jammer=False):
        gr.top_block.__init__(self, "Headless WiFi Signal Simulator", catch_exceptions=True)

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 1e6

        ##################################################
        # Blocks
        ##################################################
        # Throttle to keep CPU usage in check
        self.blocks_throttle = blocks.throttle(gr.sizeof_gr_complex, samp_rate, True)

        # Antenna Signal Sources (3 APs)
        self.ap1 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 100e3, 1.0, 0)
        self.ap2 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 200e3, 0.8, 0)
        self.ap3 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, 300e3, 0.7, 0)

        # Jammer (Noise Source)
        jammer_amp = 0.5 if use_jammer else 0.0
        self.jammer = analog.noise_source_c(analog.GR_GAUSSIAN, jammer_amp, 0)

        # Noise Adders
        self.add_noise_ap1 = blocks.add_cc()
        self.add_noise_ap2 = blocks.add_cc()
        self.add_noise_ap3 = blocks.add_cc()

        # Measurement Blocks: Complex to Mag Squared -> Moving Average -> Probe
        avg_len = 10000
        scale = 1.0 / avg_len

        self.mag_sq1 = blocks.complex_to_mag_squared(1)
        self.mag_sq2 = blocks.complex_to_mag_squared(1)
        self.mag_sq3 = blocks.complex_to_mag_squared(1)

        self.avg1 = blocks.moving_average_ff(avg_len, scale, 4000, 1)
        self.avg2 = blocks.moving_average_ff(avg_len, scale, 4000, 1)
        self.avg3 = blocks.moving_average_ff(avg_len, scale, 4000, 1)

        self.probe_ap1 = blocks.probe_signal_f()
        self.probe_ap2 = blocks.probe_signal_f()
        self.probe_ap3 = blocks.probe_signal_f()

        ##################################################
        # Connections
        ##################################################
        # Add noise to each AP to simulate realistic interference
        self.connect((self.ap1, 0), (self.add_noise_ap1, 0))
        self.connect((self.jammer, 0), (self.add_noise_ap1, 1))

        self.connect((self.ap2, 0), (self.add_noise_ap2, 0))
        self.connect((self.jammer, 0), (self.add_noise_ap2, 1))

        self.connect((self.ap3, 0), (self.add_noise_ap3, 0))
        self.connect((self.jammer, 0), (self.add_noise_ap3, 1))

        # We throttle AP1 path
        self.connect((self.add_noise_ap1, 0), (self.blocks_throttle, 0))

        # AP1 Measurement Path
        self.connect((self.blocks_throttle, 0), (self.mag_sq1, 0))
        self.connect((self.mag_sq1, 0), (self.avg1, 0))
        self.connect((self.avg1, 0), (self.probe_ap1, 0))

        # AP2 Measurement Path
        self.connect((self.add_noise_ap2, 0), (self.mag_sq2, 0))
        self.connect((self.mag_sq2, 0), (self.avg2, 0))
        self.connect((self.avg2, 0), (self.probe_ap2, 0))

        # AP3 Measurement Path
        self.connect((self.add_noise_ap3, 0), (self.mag_sq3, 0))
        self.connect((self.mag_sq3, 0), (self.avg3, 0))
        self.connect((self.avg3, 0), (self.probe_ap3, 0))

    def get_signal_strengths(self):
        p1 = self.probe_ap1.level()
        p2 = self.probe_ap2.level()
        p3 = self.probe_ap3.level()
        
        # Scaling output values normalized between 0 and 100
        return {
            'AP1': int(min(p1 * 120, 100)),
            'AP2': int(min(p2 * 120, 100)),
            'AP3': int(min(p3 * 120, 100))
        }

def main():
    print("=" * 40)
    print(" GNURadio Headless WiFi Signal Generator")
    print("=" * 40)
    jam_input = input("Enable Jammer? (y/n): ").strip().lower()
    use_jammer = True if jam_input == 'y' else False

    tb = HeadlessWiFiSimulator(use_jammer=use_jammer)

    def sig_handler(sig=None, frame=None):
        print("\nStopping simulation...")
        tb.stop()
        tb.wait()
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    print("\nSimulation running. Generating signal strengths to 'signals.txt'...")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            # Continuously update the values every second.
            time.sleep(1)
            
            signals = tb.get_signal_strengths()
            
            output_lines = [
                f"AP1 {signals['AP1']}",
                f"AP2 {signals['AP2']}",
                f"AP3 {signals['AP3']}"
            ]
            
            if use_jammer:
                output_lines.append("JAMMER 100")
                
            output_text = "\n".join(output_lines) + "\n"
            
            print("--- Latest Signals ---")
            print(output_text.strip())
            
            # Write values to signals.txt
            with open("signals.txt", "w") as f:
                f.write(output_text)
                
    except KeyboardInterrupt:
        sig_handler()

if __name__ == '__main__':
    main()
