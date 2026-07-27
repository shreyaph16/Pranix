# Pranix
 
Hyperlocal air quality intelligence system for municipal teams in Indian cities. Pranix combines spatial clustering, time-series forecasting, and causal inference to detect pollution hotspots, predict AQI spikes 24 hours in advance, and recommend field interventions ranked by estimated impact.
 
---
 
## Problem
 
City-level air quality monitoring misses neighbourhood-scale events — garbage dump fires, industrial cluster emissions, traffic congestion smog traps — because sensor networks are sparse and satellite data lacks the resolution for street-level decisions. Municipal teams cannot deploy resources (water-mist cannons, cleanup crews, traffic reroutes) without knowing where, when, and why a spike is occurring.
 
## Solution
 
Pranix processes sensor readings, satellite aerosol data, and citizen photo reports to produce three outputs:
 
1. A live hotspot map showing which neighbourhoods are currently in violation, detected via DBSCAN spatial clustering.
2. A 24-hour PM2.5 forecast per station, produced by a LightGBM model trained on lag features and weather confounders.
3. A ranked intervention table showing which municipal action has the highest estimated causal effect on PM2.5, estimated via a Doubly Robust Learner (EconML) with root cause attribution via DoWhy.
