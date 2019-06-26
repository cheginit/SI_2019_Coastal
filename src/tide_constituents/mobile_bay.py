import tide_constituents as tc
import pandas as pd


water_levels, phase, amp = tc.get_tides('20150301', '20150430', -88.2, 30.4)

pd.DataFrame({'Constituent': list(phase.keys()), 'Phase': list(phase.values()), 'Amplitude': list(amp.values())}).to_csv('constituents.csv', index=False)
water_levels[['water_level']].to_csv('water_levels.csv')
