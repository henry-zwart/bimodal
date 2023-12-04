# Weather notes

## Wind
- Datestamp is at end of observation period.
- Direcion is given in "degrees true" and refers to the
    direction the wind is coming from. i.e. 0 implies a northerly

## Rain
Hourly rain data is computationally intensive, and browser may time out when retrieving from periods of more than one year. The results are a synthesis from both "tipping bucket" and "RIG" tables. "RIG" is considered more accurate by NIWA.

Synthesis process is:

1. Look for RIG data in "RAIN_RATE" table
