# ST's pin data for Burrito's two MCUs

- `STM32H563VITx.xml` (flight, LQFP100) and `STM32H563RITx.xml` (comms, LQFP64): each pin's position, type and
  the signals it can carry.
- `IP/GPIO-STM32H56x_gpio_v1_0_Modes.xml`: the alternate-function number of each signal on each pin.

From [STM32_open_pin_data](https://github.com/STMicroelectronics/STM32_open_pin_data), commit 45c0459 ("Subset of
official release STM32CubeMX 6.19.0"), fetched 22 November 2026. BSD 3-Clause licence, kept in `LICENSE`. Unchanged.

`tools/layout/pinswap.py` checks every pin move against them, and capture step 19 takes each moved net's ADC channel
and AF number from them (stage B2, D-22Nov.25).
