import ee

# 1. Robust Initialization
# We try to initialize directly with your project ID.
try:
    ee.Initialize(project='ghost-hunter-2025')
except Exception as e:
    print(f"Warning: GEE Initialization issue: {e}")
    # If this fails, the server will error out later, but it won't crash immediately.

def get_satellite_image(lat: float, lon: float, date_from: str, date_to: str):
    """
    Fetches a cloud-free median composite image using the Harmonized Sentinel-2 collection.
    """
    try:
        # Define the Region of Interest (ROI)
        point = ee.Geometry.Point([lon, lat])
        roi = point.buffer(500) 

        # 2. Use the NEW Harmonized Collection (Fixes the Deprecation Warning)
        s2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")

        # 3. Cloud Strategy: The "Median Composite"
        # We do NOT filter by cloud percentage here. We take everything.
        # The median() reducer effectively removes clouds because clouds are bright outliers
        # that don't persist in the same pixel over 3 months.
        dataset = s2.filterDate(date_from, date_to)\
                    .filterBounds(roi)
        
        # Check if we actually found images
        count = dataset.size().getInfo()
        if count == 0:
            return {"error": "No satellite images found for this location/date range."}

        # 4. Create the Composite
        median_image = dataset.median().clip(roi)

        # 5. Calculate NDVI
        # B8 = Near Infrared (NIR), B4 = Red
        ndvi = median_image.normalizedDifference(['B8', 'B4']).rename('NDVI')
        
        # Add NDVI to the image
        result_image = median_image.addBands(ndvi)

        # 6. Extract Mean NDVI for the area
        stats = result_image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=roi,
            scale=10,
            maxPixels=1e9
        ).getInfo()

        return {
            "ndvi_mean": stats.get('NDVI'),
            "image_count": count,
            "meta": "Sentinel-2 Harmonized Median Composite"
        }

    except Exception as e:
        # Return a clean error instead of crashing the server
        return {"error": str(e)}