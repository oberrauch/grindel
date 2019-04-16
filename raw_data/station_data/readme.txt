STATION DATA FILES:
--------------------
This directory contains preprocessed station data. 
Station meta files contain station name, parameter name, data source, coordinates and elevation, index by station code. The data file contain values of one single parameter, index by time (day, month, or year) and stations as columns.

Station (meta) files:
---------------
- monthly_precip_stations.csv: list of stations which provide monthly precipation records
- monthly_temp_stations.csv: list of stations which provide (monthly mean) temperature records 
- slf_stations.csv: list of all 'SLF stations', which provide daily precipitation records

Data files:
----------------
- daily_precip_slf.csv: DataFrame of daily precipitation sums of the 'SLF stations'
- monthly_temp_jungfrau.csv: DataFrame of monthly mean temperature records from the Jungfrau station
- monthly_precip_eiger_scheidegg.csv: DataFrame of monthly precipitation sums from station Eigergletscher and Kl. Scheidegg
- monthly_precip_slf.csv: DataFrame of monthly precipitation sums of the 'SLF stations'
- yearly_precip_avg_slf.csv: DataSeries of average yearly precipitation of the 'SLF stations' over full time period available
- yearly_precip_slf.csv: DataFrame of yearly precipitation sums of the 'SLF stations'
