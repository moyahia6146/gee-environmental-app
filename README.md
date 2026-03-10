# gee-environmental-app
small mapping project for academic purposes
# 🌍 Geospatial Environmental Analysis Dashboard

A lightweight, interactive web application built with Python, Streamlit, and the Google Earth Engine (GEE) API. This tool generates scientific-quality environmental maps to support academic research, land degradation neutrality studies, and vegetation monitoring.

## 🚀 Features

The dashboard automatically generates a bounding box for any specified location and produces six research-grade maps using real-time satellite data:

* **Satellite Map:** High-resolution natural color composite using Sentinel-2 Surface Reflectance.
* **Topographic Contour Map:** Terrain elevation modeling using SRTM DEM (30m).
* **Land Degradation Map:** Vegetation health analysis and degradation classification using MODIS NDVI time series.
* **Soil Moisture Proxy Map:** Surface moisture evaluation using Sentinel-1 Radar backscatter.
* **Land Use / Land Cover (LULC):** Landscape classification using ESA WorldCover data.
* **Vegetation Change Map (2000-2025):** Long-term NDVI difference analysis using the Landsat satellite series to detect vegetation gain or loss.

## 🛠️ Technologies Used

* **Python 3.11**
* **Streamlit:** For the interactive web interface.
* **Google Earth Engine (GEE):** For cloud-based geospatial processing and satellite data retrieval.
* **geemap:** For rendering GEE layers and adding cartographic elements (scale bars, legends).

## 📊 Data Sources

This tool processes data from the following sensors:
* Sentinel-2 (Multispectral)
* Sentinel-1 (SAR)
* Landsat 7, 8, & 9
* MODIS (Terra/Aqua)
* SRTM (Shuttle Radar Topography Mission)

## 💻 How to Run Locally

If you wish to run this tool on your local machine, follow these steps:

1. Clone this repository to your local machine.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   
