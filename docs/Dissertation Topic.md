# Dissertation Topic

### Problem

What musical features drive song popularity?



### Research Questions

1. How have the structural determinants of song popularity evolved over time in contemporary music?

2\. How accurately can song popularity be predicted using Spotify audio features?



### Topic

Predicting Song Popularity from Spotify Audio Features: How Determinants Change Over Time



### Dataset(s)

https://www.kaggle.com/datasets/solomonameh/spotify-music-dataset?resource=download



### Similar Papers

* https://royalsocietypublishing.org/rsos/article/5/5/171274/94110 - similar predictors, clustering, UK charts only (2018)
* https://www.tandfonline.com/doi/full/10.1080/23270012.2023.2239824#d1e507 - very similar, different methodology, Indonesia only (2023)
* https://people.stat.sc.edu/Hitchcock/jds1040.pdf - genre popularity, TS (2022)
* https://dbis-informatik.uibk.ac.at/sites/default/files/2019-12/zangerle\_ismir\_19.pdf - different dataset, only audio information (2019)





### Proposed Solution

* Temporal regression (a baseline model + an enhanced one (XGBoost?) for comparison)
* Predicting song popularity based on audio features and release date
* comparing feature importance across time periods to identify how the drivers of popularity evolved

