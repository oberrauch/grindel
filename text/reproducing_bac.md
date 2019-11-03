# Proof of concept, again?!

In the following paragraphs I try to summarise what I have done so far. More or less I followed reproduced the findings from my Bachelor thesis, to see where we are at...

**In a nutshell:** It works, but not as well as we would like it to.

## Calibration

**Background and tuning parameters** 

The main novelty of the original volume/area scaling model by Marzeion, et. al. (2012) is the calibration of the temperature index mass balance model. The underlying hypothesis is, that neighbouring glaciers will be in equilibrium state around the same time. Given the *equilibrium year* $t^*$, the temperature sensitivity $\mu(t^*) =: \mu^*$ is computed assuming a net-zero mass balance for the 31-year period centred around $t^*$. However, those parameters are based on statistical optimisation and not to be understood as physical temperature sensitivity and actual year in which the glacier was in equilibrium. On the other hand, this allows me to use $t^*$ as an additional calibration parameter.

Glen-Nye flow law relates the stress $\tau$ to the ice strain rate $\dot{\epsilon}$, as $\dot{\epsilon} = A\cdot\tau^n$. The A-parameter (also kwon as creep parameter) in the OGGM combines a lot of different ice mechanical processes (ice temperature, lateral drag, debris content, etc.) into one single tuning variable.

The second tuning variable is the precipitation scaling factor. Climate models tend to underestimate the precipitation onto glaciers. Additional mass input by avalanches from adjacent slopes, snow drift, etc., is not reflected in the HISTALP data set. The precipitation parameter is only changed for the model run and not for the model calibration, i.e., all models use the same temperature sensitivity $\mu^*$ for the same year.

**Calibration reference**

The performance of the model is measured by the correlation  and the RMSD (root mean squared error) between the modeled and observed glacier length. The length data record (obtained from [glamos.ch](https://doi.glamos.ch/data/lengthchange/lengthchange.csv)) contains yearly glacier length changes from 1880 until 2017. Some data points are missing, at the end of the 19th century (1882 - 1893), around the time of both world wars, and between 2000 and 2013. To obtain absolute values, the length change is offset with the RGI length of 2003. Since there is no measurement from 2003, the values is obtained by a linear extrapolation of the previous 11 years with records (1989 - 1999).

![Length change measurement time series](/Users/oberrauch/work/grindelwald/figures/repoduce_bac/length.pdf)

**Multi-parameter, multi-object calibration**

The goal is to have a glacier model which can reproduce the observed length changes with decent accuracy. Since we have three tuning parameters and two performance scores, it is not possible to apply a simple minimisation algorithm. Instead, I decided on a fixed parameter space based on previous experiments. The equilibrium year $t^*$ ranges from 1935 to 1960 in 5-year steps, the precipitation scaling factor ranges from 1.0 to 1.75 in steps of 0.25, whereas the scaling factor for the creep parameters spans over two orders of magnitude and assumes the following values: 0.1, 0.5, 1.0 2.0, 10.0.

![Multi-parameter, multi-object calibration](/Users/oberrauch/work/grindelwald/figures/repoduce_bac/calibration.pdf)

**Results**

The equilibrium year $t^*$ has the least effect on the model performance, compared with the other two parameters. A higher creep parameter result in a more fluid (less viscose) glacier behaviour, since $A$ is a linear parameter in the Glen-Nye flow law. This makes the glacier respond faster and stronger to the given climatic input. More precipitation and the accompanied higher mass turnover has a similar effect. Hence, both parameters are somewhat direct proportional to the correlation coefficient between modeled and measured glacier length change and indirect proportional to the root mean squared difference between the length records.

However, there are is a set of parameters which produces reasonable model results. Hereby, reasonably is arbitrarily defined by me as a correlation coefficient higher or equal to 0.75 and a RMSD below 300 m. For the following experiments I used the following parameter set

- (Model) equilibrium year $t^*:$ 1945
- Model bias $\beta^*$: 0
- Precipitation scaling factor: 1.75 (default value for HistAlp data set)
- Creep parameter scaling factor: 1, i.e. default A param of 2.4 $\cdot 10^{-25}\ \mathrm{s}^{-1} \mathrm{Pa}^{-1}$

**Outlook/ToDo's:**

- [ ] Repeat the calibration with a finer subset between the best parameter?! Overfitting?!

- [ ] Use all "good" parameter sets and run some sort of ensemble model... Runtime?!

## Location of cave entrances

After a successful calibration, the first step is to locate the cave entrances along the flowline. Marc Luetscher supplied us with a list of the GPS coordinates and the elevation of each cave entrance.

| Entrance | Longitude [°E, WGS84] | Latitude [°N, WGS84] | Elevation [m asl.] |
| -------- | --------------------- | -------------------- | ------------------ |
| E1       | 8.0843                | 46.6241              | 1601               |
| E2       | 8.08983               | 46.6181              | 1885               |
| E3       | 8.08995               | 46.6188              | 1794               |
| E5       | 8.08989               | 46.6193              | 1740               |
| E4       | 8.08991               | 46.6196              | 1697               |

The OGGM operates on a local grid, different for each glacier. So first of all, the (main) flowline grid points have to be translated into WGS84 coordinates. The next step is to find the closest (two) grid points to each entrances. Given that I tried to project them normal onto the flowline, to estimate ice thickness between grid points. As it turns out, the entrances E2 - E5 are located between grid point °47 and °48, whereas the entrance E1 is almost exactly aligned with grid point °54. **Note:** this may change if the flowline(s) are computed differently (e.g., based on a different DEM). **Note #2:** What about the distance to the flowline... The OGGM glacier surface is flat, but the actual glacier is not. 

![Location of cave entrances along the main model flowline](/Users/oberrauch/work/grindelwald/figures/repoduce_bac/caves_location.pdf)

##Results

Give all that, we are now able to compute the evolution of ice thickness at the cave entrances. Again, Marc Luetscher provided us with measurements of the glacier surface elevation in vicinity of the cave entrances, in addition to the years when the different entrances opened (i.e., glacier surface below entrance). If the model can reproduce these measurements to a given degree of accuracy (the degree is still to be defined), we can proceed with the actual "climate reconstruction" based on the speleothem records.

![Ice thickness at cave entrances E2, E3, E5 and E4](/Users/oberrauch/work/grindelwald/figures/repoduce_bac/ice_thickness.pdf)

The results looks quite promising, at first glance. All cave entrances are above the modeled bedrock, which is a win compared to the results of my Bachelor thesis. However, the ice at this point is still not thick enough to close the uppermost entrance E2.

![Ice coverage of the cave entrances E2, E3, E5 and E4](/Users/oberrauch/work/grindelwald/figures/repoduce_bac/caves_open.pdf)

From a more general point of view, the modeled thinning is slower than the observed one. This is even more drastic if we consider the thicker actual glacier. While the modeled glacier retreat/melting is to slow it happens a few years too early.

![](/Users/oberrauch/work/grindelwald/figures/repoduce_bac/glacier_cross_section.pdf)

## Discussion

Here are some possible explanations and/or suggestion for improvement:

- We should have a closer look at the modeled bed shape in the tongue area. A steeper (and narrower) bed should increase the ice thickness. Eventually, we have to compute the actual bed shape from a more recent DEM, where the glacier is already gone...
- The steep rock canyon reflect a lot of incoming radiation, which can enhance the ice thinning in comparison to a purely temperature driven glacier melt.
- Use relative elevation of cave entrances above the bedrock, to eliminate the bedrock elevation as variable. *ToDo: ask Marc if he has such measurements.*
- ... it's late and I'm tired, so I'm certainly missing some obvious points.

**So, what next?!**

