# Tuning the model - a first attempt

I tried to calibrate the model by tuning the precipitation scaling factor (`prcp_scaling_factor`) as well as the creep parameter (`inversion_glen_a`  & `glen_a`) in order to reproduce the observed length changes.

Changing the precipitation scaling factor calls for a new mass balance calibration, resulting in different *equilibrium* years $t^*$ and temperature sensitivities $\mu^*$.

While the model runs over the entire HistAlp climate period (1850 - 2014), the *performance parameters* are computed for the period between 1894 and 2003 (where there are reliable observations).

The performance of the model is measured by the correlation between the modeled and observed length changes as well as the root mean squared deviation between the modeled and observed length change anomalies (i.e., departures from the respective mean). **Note:** I'm not to happy with the chosen parameters. Neither of the two measures accounts for a temporal shift, which can lead to misleadingly bad scores.

There is no identifiable pattern, hence no clear choice for the best parameters.

For higher values of Glen's *A* parameter the correlation between modeled and observed length changes increases. Highest correlation is found for a creep parameter 20-times as high as the default value ($2.4 \cdot 10^{-24}\ \mathrm{s^{-1}Pa^{-3}}$ ), which seems non physical. It seems as if the *default* model glacier is too inert and the ice flows too slow...

![Correlation matrix](../figures/glen_a/correlation.pdf)

On the other hand, the amplitude of length changes increases with increasing *A* parameter. Since the modeled length changes are already larger than the observed one, this is not really helping... But as mentioned above, the RMSD is not the best quantification score.

![Correlation matrix](../figures/glen_a/rmsd.pdf)

The following exemplary figures illustrate the model behaviour for a precipitation scaling factor of 1 and 1.75, respectively. Thereby the creep parameters varies over two orders of magnitude (i.e., $2.4 \cdot [10^{-25},\ 10^{-24},\ 10^{-25}] \ \mathrm{s^{-1}Pa^{-3}}$).

![Length changes for precipitation factor 1](../figures/glen_a/prcp_scaling_factor_1_00.pdf)

![Length changes for precipitation factor 1.75](../figures/glen_a/prcp_scaling_factor_1_75.pdf)

 