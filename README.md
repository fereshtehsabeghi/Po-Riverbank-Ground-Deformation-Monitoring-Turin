# Po Riverbank Ground Deformation Monitoring — Turin

**An early-warning triage tool for urban infrastructure monitoring, using free Copernicus Sentinel-1 InSAR data.**

![Full Scene](figures/full scene.jpg)
![Screenshot](figures/Screenshot 2026-07-06 213046.jpg)

## Overview

This project uses ground deformation data from the European Ground Motion Service (EGMS) — derived from Sentinel-1 InSAR processing — to identify statistically significant zones of ground movement along the Po riverbank corridor in Turin, Italy. These deformation hotspots are then cross-referenced against OpenStreetMap infrastructure data and Italy's official hydrogeological hazard maps (ISPRA PAI) to flag buildings and structures that may be exposed to active, ongoing ground instability that isn't necessarily captured by static, periodically-updated hazard classifications.

The corridor covers Borgo Po, Murazzi, Gran Madre, Corso Moncalieri, and down toward the Moncalieri municipal boundary, plus the Basse di Stura area to the north.

## Motivation

The Po riverbank is one of the most visually striking and expensive residential corridors in Turin, and it's also an area where surface signs of soil fragility (exposed tree roots, visible bank erosion) are common. Official Italian hazard maps (ISPRA's PAI framework) classify flood and landslide risk at a broad, static level. This project asks: **does continuous, satellite-derived deformation data agree with those official classifications, or does it reveal risk that the static maps miss?**

## Repository Structure

```text
├── README.md
├── /script
│   ├── check_distances.py          # Distance-to-nearest-structure for each hotspot
│   ├── export_to_kepler.py         # GeoJSON export helper
│   ├── extract_infrastructure.py   # OSM building/infrastructure query + spatial join
│   ├── fix_kepler_export.py        # Reproject + clean layers for Kepler.gl
│   ├── hotspot_analysis.py         # Getis-Ord Gi* statistical hotspot detection
│   ├── process_ispra.py            # Auto-clip and validate against ISPRA PAI hazard maps
│   └── spatial_triage.py           # Clip raw EGMS data to river corridor buffer
└── /figures                        # Kepler.gl screenshots, annotated risk zone maps
