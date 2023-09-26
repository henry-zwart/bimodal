# Analysis and visualisation of bike counter data in Wellington

## Data Sources

Data is imported from the [WCC transport projects website](https://www.transportprojects.org.nz/cycle-data/#showdata/electronic/all/2023-08-01) by DVC. It does look as though the file URLs may be changed occasionally, so this approach might need to change.

We are currently tracking annual raw count data files in CSV format from 2018-2023.

## Plan

- [x] Set up data sources
- [x] Move data into a sqlite database
- [ ] Explore data
    - What's the uptick per-month across the years?
    - Have the times people are cycling changed, or stayed the same? e.g. have 7am numbers gone up while others have stayed consistent?
    - Do people prefer to cycle in one direction?
    - What's the first derivative of uptick? Second derivative?
    - What's the impact of a new cycle lane opening, on own numbers, on other path numbers?
    - What time of year do people typically cycle?
    - Does the numbers vs. time of year relationship depend on the path taken?
    - Are there consistent relationships between times of year? e.g. twice as many people cycle in the summer
    - Can we predict the number of bike trips in the next three months given previous
        data?
    - How does the number of bike trips in a given hour change w.r.t. the weather?
        - Wind?
        - Rain?
        - Sun?
        - Does the daily number of trips change?
        - Does the time people travel change? e.g. if its raining, do people travel later? Earlier?
- [ ] ...


## Database
Tables include:
- Site: site id and name as recorded in the count data
- Count: hourly incoming (toward CBD) and outgoing (away from CBD) counts at each location
- Rain: daily rainfall measurements in millimeters
- Wind: hourly speed and direction (with standard dev. included)
- Temperature: hourly min/max/avg temperature, and percentage relative humidity measurements

Weather measurements taken from Kelburn weather station, gathered through NIWA API.

**Tables**
- Site
    - site_id:          INTEGER
    - site_name:        TEXT
- Count
    - count_id:         INTEGER
    - site_name:        TEXT
    - record_time:      TEXT
    - count_incoming:   INTEGER
    - count_outgoing:   TEXT
    - year:             INTEGER
    - month:            INTEGER
    - day:              INTEGER
    - hour:             INTEGER
    - weekday:          INTEGER
- Rain
    - rain_record_id:   INTEGER
    - record_time:      TEXT
    - amount:           FLOAT
    - year:             INTEGER 
    - month:            INTEGER
    - day:              INTEGER
- Wind
    - wind_record_id:   INTEGER
    - record_time:      TEXT
    - direction_deg:    INTEGER
    - speed_ms:         FLOAT
    - direction_std:    FLOAT
    - speed_std:        FLOAT
    - period:           FLOAT
    - year:             INTEGER
    - month:            INTEGER
    - day:              INTEGER
    - hour:             INTEGER
- Temperature
    - temperature_record_id:    INTEGER
    - record_time:              TEXT
    - temp_max_c:               FLOAT
    - temp_min_c:               FLOAT
    - temp_avg_c:               FLOAT
    - rel_humidity_perc:        INTEGER
    - year:                     INTEGER
    - month:                    INTEGER
    - day:                      INTEGER
    - hour:                     INTEGER


## Ideas

- [ ] Create a visualisation of cycle routes over a year. Show a map with the different
        counters, and draw sprites travelling between the counters at the recorded rate.