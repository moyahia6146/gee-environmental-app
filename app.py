import streamlit as st
import ee
import geemap.foliumap as geemap
import datetime
import json
from google.oauth2 import service_account

# Streamlit Page Setup
st.set_page_config(layout="wide", page_title="GEE Environmental Analysis", page_icon="🌍")

st.title("🌍 Geospatial Environmental Analysis Dashboard")
st.markdown("Generate scientific-quality environmental maps using Google Earth Engine.")

# GEE Authentication (Cloud Service Account)
@st.cache_data
def ee_authenticate():
    try:
        key_dict = json.loads(st.secrets["EARTHENGINE_TOKEN"])
        credentials = service_account.Credentials.from_service_account_info(key_dict)
        scoped_credentials = credentials.with_scopes(['https://www.googleapis.com/auth/earthengine'])
        ee.Initialize(credentials=scoped_credentials, project=key_dict['project_id'])
    except Exception as e:
        st.error(f"فشلت المصادقة السحابية: {e}")
        st.stop()

ee_authenticate()

# Sidebar Inputs
st.sidebar.header("📍 Study Area Parameters")
lat = st.sidebar.number_input("Latitude", value=34.0522, format="%.4f")
lon = st.sidebar.number_input("Longitude", value=-118.2437, format="%.4f")
radius_km = st.sidebar.number_input("Area radius (km)", value=10.0, min_value=1.0, max_value=100.0)

st.sidebar.header("📅 Timeframe & Filters")
start_date = st.sidebar.date_input("Start Date", datetime.date(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.date(2023, 12, 31))
cloud_cover = st.sidebar.slider("Cloud cover threshold (%)", 0, 100, 20)

start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

# Generate Bounding Box
poi = ee.Geometry.Point([lon, lat])
roi = poi.buffer(radius_km * 1000).bounds()

st.sidebar.info("Adjust parameters and the maps will update automatically.")

# Helper Functions
def add_map_elements(m, title):
    m.add_title(title, font_size="16px", align="center")
    m.add_scale_bar()
    return m

# Map 1: Satellite Map (Sentinel-2)
st.header("1. Satellite Map (Sentinel-2 RGB)")
try:
    s2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
        .filterBounds(roi) \
        .filterDate(start_date_str, end_date_str) \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud_cover)) \
        .median() \
        .clip(roi)

    vis_params_s2 = {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000}
    
    m1 = geemap.Map(center=[lat, lon], zoom=12)
    m1.addLayer(s2, vis_params_s2, "Sentinel-2 RGB")
    m1.addLayer(roi, {'color': 'red'}, "Study Area", False, 0.5)
    add_map_elements(m1, "Sentinel-2 Natural Color Composite")
    m1.to_streamlit(height=500)
except Exception as e:
    st.error(f"Error generating Satellite Map: {e}")

# Map 2: Topographic Contour Map (SRTM DEM)
st.header("2. Topographic Contour Map")
try:
    dem = ee.Image("USGS/SRTMGL1_003").clip(roi)
    hillshade = ee.Terrain.hillshade(dem)
    
    vis_params_dem = {'min': 0, 'max': 3000, 'palette': ['006633', 'E5FFCC', '662A00', 'D8D8D8', 'F5F5F5']}
    
    m2 = geemap.Map(center=[lat, lon], zoom=12)
    m2.addLayer(hillshade, {}, "Hillshade", opacity=0.5)
    m2.addLayer(dem, vis_params_dem, "SRTM DEM", opacity=0.7)
    m2.add_colorbar(vis_params_dem, label="Elevation (m)")
    add_map_elements(m2, "Topographic Map (SRTM DEM)")
    m2.to_streamlit(height=500)
except Exception as e:
    st.error(f"Error generating Topographic Map: {e}")

# Map 3: Land Degradation Map (MODIS NDVI)
st.header("3. Land Degradation Map")
try:
    modis = ee.ImageCollection("MODIS/061/MOD13Q1") \
        .filterBounds(roi) \
        .filterDate(start_date_str, end_date_str) \
        .select('NDVI') \
        .median() \
        .multiply(0.0001) \
        .clip(roi)
        
    degradation = ee.Image(1) \
        .where(modis.lt(0.2), 3) \
        .where(modis.gte(0.2).And(modis.lt(0.5)), 2) \
        .where(modis.gte(0.5), 1) \
        .clip(roi)
        
    deg_palette = ['00FF00', 'FFFF00', 'FF0000']
    deg_legend = {'Healthy Vegetation': '00FF00', 'Moderate Degradation': 'FFFF00', 'Severe Degradation': 'FF0000'}
    
    m3 = geemap.Map(center=[lat, lon], zoom=12)
    m3.addLayer(degradation, {'min': 1, 'max': 3, 'palette': deg_palette}, "Land Degradation")
    m3.add_legend(title="Degradation Status", legend_dict=deg_legend)
    add_map_elements(m3, "Land Degradation Map (MODIS NDVI)")
    m3.to_streamlit(height=500)
except Exception as e:
    st.error(f"Error generating Land Degradation Map: {e}")

# Map 4: Soil Moisture Map (SMAP / Sentinel-1)
st.header("4. Soil Moisture Map")
try:
    s1 = ee.ImageCollection("COPERNICUS/S1_GRD") \
        .filterBounds(roi) \
        .filterDate(start_date_str, end_date_str) \
        .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')) \
        .select('VV') \
        .median() \
        .clip(roi)
        
    moisture_class = ee.Image(1) \
        .where(s1.lt(-15), 4) \
        .where(s1.gte(-15).And(s1.lt(-10)), 3) \
        .where(s1.gte(-10).And(s1.lt(-5)), 2) \
        .where(s1.gte(-5), 1) \
        .clip(roi)
        
    sm_palette = ['0000FF', '00FFFF', 'FFA500', '8B4513']
    sm_legend = {'High Moisture': '0000FF', 'Moderate Moisture': '00FFFF', 'Low Moisture': 'FFA500', 'Very Dry Soil': '8B4513'}
    
    m4 = geemap.Map(center=[lat, lon], zoom=12)
    m4.addLayer(moisture_class, {'min': 1, 'max': 4, 'palette': sm_palette}, "Soil Moisture Index")
    m4.add_legend(title="Soil Moisture", legend_dict=sm_legend)
    add_map_elements(m4, "Soil Moisture Map (S1/SMAP Proxy)")
    m4.to_streamlit(height=500)
except Exception as e:
    st.error(f"Error generating Soil Moisture Map: {e}")

# Map 5: Land Use / Land Cover Map
st.header("5. Land Use / Land Cover Map")
try:
    worldcover = ee.ImageCollection("ESA/WorldCover/v200").first().clip(roi)
    
    lulc = worldcover.remap(
        [10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100],
        [1,  2,  2,  3,  4,  5,  5,  1,  1,  1,  1] 
    ).clip(roi)
    
    lulc_palette = ['228B22', 'ADFF2F', 'FFD700', 'A9A9A9', 'D2B48C']
    lulc_legend = {
        'Forest/Other': '228B22', 
        'Pasture/Rangeland': 'ADFF2F', 
        'Agricultural Land': 'FFD700', 
        'Built-up': 'A9A9A9',
        'Bare Soil / Degraded': 'D2B48C'
    }
    
    m5 = geemap.Map(center=[lat, lon], zoom=12)
    m5.addLayer(lulc, {'min': 1, 'max': 5, 'palette': lulc_palette}, "LULC")
    m5.add_legend(title="Land Use / Land Cover", legend_dict=lulc_legend)
    add_map_elements(m5, "Land Use / Land Cover Map")
    m5.to_streamlit(height=500)
except Exception as e:
    st.error(f"Error generating LULC Map: {e}")

# Map 6: Vegetation Change Map (2000-2025)
st.header("6. Vegetation Change Map (2000-2025)")
try:
    l7_2000 = ee.ImageCollection("LANDSAT/LE07/C02/T1_L2") \
        .filterBounds(roi) \
        .filterDate('2000-01-01', '2000-12-31') \
        .median()
    
    ndvi_2000 = l7_2000.normalizedDifference(['SR_B4', 'SR_B3']).rename('NDVI')
    
    l8_2025 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2") \
        .filterBounds(roi) \
        .filterDate('2024-01-01', '2025-12-31') \
        .median()
        
    ndvi_2025 = l8_2025.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
    
    ndvi_diff = ndvi_2025.subtract(ndvi_2000).clip(roi)
    
    change_class = ee.Image(2) \
        .where(ndvi_diff.lt(-0.1), 1) \
        .where(ndvi_diff.gt(0.1), 3) \
        .clip(roi)
        
    change_palette = ['FF0000', '808080', '00FF00']
    change_legend = {'Negative Change (Loss)': 'FF0000', 'No Significant Change': '808080', 'Positive Change (Gain)': '00FF00'}
    
    m6 = geemap.Map(center=[lat, lon], zoom=12)
    m6.addLayer(change_class, {'min': 1, 'max': 3, 'palette': change_palette}, "Vegetation Change")
    m6.add_legend(title="Vegetation Change (2000-2025)", legend_dict=change_legend)
    add_map_elements(m6, "Vegetation Change Map")
    m6.to_streamlit(height=500)
except Exception as e:
    st.error(f"Error generating Vegetation Change Map: {e}")

st.sidebar.header("💾 Export Data")
st.sidebar.info("To export GeoTIFFs, use the `geemap.ee_export_image` function in your local environment.")
        
