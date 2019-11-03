WP1: Data Compilation and Preparation
-------------------------------------
1. Digital Elevation Model (DEM)
   - SRTM: OGGM default data set, with a resolution of (approx.) 90m. The vertical error (accuracy) is reported to be less than 16m (http://srtm.csi.cgiar.org/).
   - SwissTopo:
         - DSM: high accuracy aerial orthophotos
           Price on request, which suggests high costs. The resolution is probably an overkill for the OGGM anyway, considering all the other assumptions.
        - swissALTI3D: Resolution between 2m, 5m, or 10m with an accuracy of 1-3m at elevations above 2000m a.s.l. Price for the "Gemeinde Grindelwald" tile: CHF 519.75
        - DHM25: Digitised height from National Map 1:25 000 resulting in a product with a resolution of 25m. The accuracy depends on the map, but can be considered to be between 3m an 8m in alpine regions. same time as glacier outlines! Price for the "Gemeinde Grindelwald" tile: CHF 56.75
        - DHM25/200: Free version of the above, but with a lower resolution of 200m (same accuracy though). I'd say the canyon at the tongue area is not properly resolved in this dataset.
      - EU-DEM: hybrid product of SRTM and ASTER, resulting in a product with a resolution of 25m and an accuracy of 7m (RMSE). https://www.eea.europa.eu/data-and-maps/data/copernicus-land-monitoring-service-eu-dem
      - Maybe Marc has a mapping of the tongue area (TODO: send email to Marc), alternatively it would be possible to go there and measure it ourselfs.

2. Glacier outlines

   - GLIMS/RGI:

     The RGI dataset has glacier outlines from 5 different dates between 1850 and 2009. All outlines include an area (estimate) given by the shapefile.

     * 1850.09.01: Field and aerial photo reconstruction + Siegfriedmap, transfer to topographic map (1:25000). Manual digitisation from transparent paper with topo map in background, using ArcInfo and ArcGIS and later transformation to shape files; Field and aerial photo
     * 1973.09.01: The outlines were directly transferred and digitized from aerial photography to 1:25000 topo maps. In September 1973 favorable conditions for glacier
     * 1998.08.31: TM4/TM5 ratio; Glaciers were automatically mapped from TM raw data using two thresholds: TM3/TM5 > 2.1 and TM1 > 53. The glacier map was smoothed with a 3 by 3 median filter. After raster-vector conversion gross errors were manually removed (water, lakes)
     * 2003.08.06:All glaciers are classified in the main processing stage with a thresholded ratio image and an additional threshold to provide the classification in shadow regions (e.g. Paul and Kaeaeb, 2005); All glaciers are classified in the main processing stage wit
     * 2008.09.30: Glacier outlines were digitized manually in ArcGIS based on SWISSIMAGE Level 2 (swisstopo) imagery. Glacier polygons were coded and named according the outlines of 1973.
     * 2009.09.15: SwissImage L2 aerial orthophotos, manual digitisation; Glacier outlines were digitised manually from high-resolution aerial photography (swissimage level 2; 50cm resolution) acquired in September 2008 (34 glaciers); 2009(354 glaciers); 2010 (708 glaciers)
     
   - Topographic maps: The Swiss federal geoportal has digitised versions of different topographic maps from 1870, 1987, 1993, and 2016 (see http://map.geo.admin.ch/).
   
   * Orthophoto(s): TODO

3. Glacier length variations:
   - VAW: The Laboratory of Hydraulics, Hydrology and Glaciology (Versuchsanstalt für Wasserbau, Hydrologie und Glaziologie) at the ETH Zürich supplies a dataset of yearly measurements of Glacier length variations from 1880 until 2016 (http://swiss-glaciers.glaciology.ethz.ch/download/obgrindelwald.html)
   - additional data?!

4. Glacier thickness data
   - GPR tongue area: 
   - other measurements?!

5. Recent climate data
   - HISTALP
   - Digitalisierung und Homogenisierung von historische Klimadaten des Swiss NBCN (Klima-Messnetzwerk) http://www.meteoschweiz.admin.ch/home/mess-und-prognosesysteme/datenmanagement/historische-meteorologische-messdaten.html  	
   - Nearby stations SLF
     - SLF: Schnee + Temperature
       - Schmidigen-Bidmeren 2111 m (https://www.slf.ch/avalanche/stations/IMIS_FIR2_DE.pdf)
       - Russisprung 2150 m (https://www.slf.ch/avalanche/stations/IMIS_LHO2_DE.pdf)
       - Itramen 2162 m (https://www.slf.ch/avalanche/stations/IMIS_MAE2_DE.pdf)
     - SLF: Wind + Temperatur
       - Lauberhorn 2190 m (https://www.slf.ch/avalanche/stations/IMIS_LHO3_DE.pdf)
       - Männlichen 2341 m (https://www.slf.ch/avalanche/stations/IMIS_MAN1_DE.pdf)
     - Contact at SLF: imis@slf.ch
   - Nearby stations MeteoSwiss
     - Interlaken 577m (http://www.meteoschweiz.admin.ch/product/input/smn-stations/docs/INT.pdf)
     - Lauterbrunnen 815m (http://www.meteoschweiz.admin.ch/product/input/smn-stations/docs/LTB.pdf)
     - Jungfraujoch 3580m (http://www.meteoschweiz.admin.ch/product/input/smn-stations/docs/JUN.pdf)

6. Paleoclimate data

   - ...?!

7. "Non scientific" data

   - There are several nearby webcam stations (see http://www.kaikowetter.ch/berneroberlando.html), none of which have a direct view of the Upper Grindelwald Gletscher.

   - Book: "Die Grindelwaldgletscher - Kunst und Wissenschaft", by Zumbühl et. al. (as editor)

     The book includes historic paintings and photographs used as length/extension estimates for both the Upper and Lower Grindelwald Glaciers, as well as additional written sources (like historic documents, letters, ...).

     - Chapter 3: The History of the Upper Grindelwald Glacier since the mid 13th century (p. 115 - 148)
       - Early references from the Middle Ages until the 15th century
         - no usefull source for a sensible topographic reconstruction
         - some written references, glacier used as landmark
       - Glacier history in the 16th and 17th century
         - potential short melting period around 1540 (Strasser, 1890; Gruner 1760), glacier retreat behind the "Felsnollen" (LK 649.200/164.425)
         - strong advance around end 16th/begin of 17th century, with maximum glacial extend all the way to the "Bägelbach" (around 1600-1620)
         - first graphical repesentation 1669 by A. Kauw, shows reduce glacier volume and a retreated tongue (700-800m estimated since 1600); side note states that the glacier was advancing again
         - oscillating behavior during the last 14 years of the 17th century
       - Glacier history in the 18th century until 1768: possible advance starting around 1703 and lasting until the 1720ies
       - Advance between 1768 and 1777/78
         - strong advance starting in 1768, around 50-70 m/yr?!
         - definitely over the Felsnollen and down to the Gletschersand
         - maximal extend almost to lowest moraine (1600) near Bärgelbach
         - extend of advance not fully clear, since initial state of the glacier (1768) unknown; probably around 400-500m in those 10 years
       - Melting phase between 1779 and 1803: retreat of 150m in 1786 since last maximum in 1776/77/78
       - ...