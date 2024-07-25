import os
import math
import argparse

def meters_to_latitude_degrees(meters):
    # 1 degree of latitude is approximately 111.32 kilometers
    return meters / 111320

def meters_to_longitude_degrees(meters, latitude):
    # 1 degree of longitude in meters varies with latitude
    # 1 degree of longitude = 111.32 km * cos(latitude in radians)
    return meters / (111320 * math.cos(math.radians(latitude)))

def create_kml_outline(center_lat, center_lon, size_meters):
    half_size_lat_deg = meters_to_latitude_degrees(size_meters) / 2.0
    half_size_lon_deg = meters_to_longitude_degrees(size_meters, center_lat) / 2.0

    # Calculate the corners of the square
    tl_lat = center_lat + half_size_lat_deg
    tl_lon = center_lon - half_size_lon_deg

    br_lat = center_lat - half_size_lat_deg
    br_lon = center_lon + half_size_lon_deg
    
    tr_lat, tr_lon = tl_lat, br_lon
    bl_lat, bl_lon = br_lat, tl_lon


    kml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>Square Outline</name>
      <Style>
        <LineStyle>
          <color>ff0000ff</color> <!-- Blue color -->
          <width>10</width> <!-- Line width -->
        </LineStyle>
        <PolyStyle>
          <color>00ffffff</color> <!-- Transparent fill -->
          <fill>0</fill> <!-- No fill -->
        </PolyStyle>
      </Style>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>
              {tl_lon},{tl_lat},0
              {tr_lon},{tr_lat},0
              {br_lon},{br_lat},0
              {bl_lon},{bl_lat},0
              {tl_lon},{tl_lat},0
            </coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
  </Document>
</kml>'''

    # Write to a KML file in the current directory
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "square_outline.kml"), "w") as file:
        file.write(kml_content)

    print("*.kml file 'square_outline.kml' created successfully with:")
    print(f"Top Left: {tl_lat}, {tl_lon}")
    print(f"Bottom Right: {br_lat}, {br_lon}")

    return (tl_lat, tl_lon), (br_lat, br_lon)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--center_lat', type=float, help='Center latitude', required=True)
    parser.add_argument('--center_lon', type=float, help='Center longitude', required=True)
    parser.add_argument('--size_meters', type=float, help='Size of square in meters', required=True)

    args = parser.parse_args()

    create_kml_outline(args.center_lat, args.center_lon, args.size_meters)

