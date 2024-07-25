from generate_images.Utils_KML.writeKML import create_kml_outline
from generate_images.Utils_KML.crop_red_sqaure import crop_out_segments
import subprocess

def run_workflow(center_lat, center_lon, size_meters):
    print()
    tr_coords, br_coords = create_kml_outline(center_lat, center_lon, size_meters)
    print("\nA *.kml has been created with the outline of the square.")
    print("Navigate to google earth pro and load the KML file by")
    print("using file -> open -> select your *.kml file.")
    print("Ensure layers such as roads, buildings, 3D, etc. are off.")
    print("Zoom in to the square then click view -> reset -> tilt and compass.")
    print("Export the current view at max resolution.")
    print("Once done, enter the image path below.\n\n")
    input_image_path = str(input("Enter image path Here: "))
    print()

    crop_out_segments(input_image_path, tr_coords, br_coords)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--center_lat', type=float, help='Center latitude', default = 43.913418)
    parser.add_argument('--center_lon', type=float, help='Center longitude', default = -72.657288)
    parser.add_argument('--size_meters', type=float, help='Size of square in meters', default = 3500)

    args = parser.parse_args()

    run_workflow(args.center_lat, args.center_lon, args.size_meters)
