import arcpy
import os

# Global variable for the output folder
output_folder = r"C:\Users\as425\Documents\GIS Programming\westnileoutbreak\Output"
gdb_path = r"C:\Users\as425\Documents\GIS Programming\westnileoutbreak\WestNileOutbreak\WestNileOutbreak.gdb"

def setup():
    # Set up the workspace and environment settings
    arcpy.env.workspace = r"C:\Users\as425\Documents\GIS Programming\westnileoutbreak\WestNileOutbreak\WestNileOutbreak.gdb"
    arcpy.env.overwriteOutput = True
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

def buffer(layer_name, buf_dist):
    # Buffer the incoming layer by the buffer distance
    output_buffer_layer_path = f"{output_folder}\\buf_{layer_name}.shp"
    print(f"Buffering {layer_name} at {buf_dist} to generate {layer_name}")

    arcpy.analysis.Buffer(
        layer_name,
        output_buffer_layer_path,
        buf_dist,
        "FULL",
        "ROUND",
        "ALL")
    return output_buffer_layer_path

def intersect(buffer_layer_list):
    #Intersect the 4 buffered layers and intersect them together.
    lyr_intersect = input("Enter the name for the intersect output layer name: ")
    lyr_intersect_path = f"{gdb_path}\\{lyr_intersect}"
    print(f"Intersecting {buffer_layer_list} to generate {lyr_intersect} storing to {lyr_intersect_path}")

    arcpy.analysis.Intersect(
        in_features=buffer_layer_list,
        out_feature_class=lyr_intersect_path,
        join_attributes="ALL",
        cluster_tolerance=None,
        output_type="INPUT"
    )
    return lyr_intersect

def spatial_join(Building_Addresses, lyr_intersect):
    # Combine the intersected layer with the address layer
    join_layer_path = f"{gdb_path}\\Address_Join_Intersect"
    print(f"Performing spatial join with {Building_Addresses} as target and {lyr_intersect} as join feature.")

    arcpy.analysis.SpatialJoin(
        target_features=Building_Addresses,
        join_features=lyr_intersect,
        out_feature_class=join_layer_path,
        join_type="KEEP_COMMON",  # Keep only addresses within intersect area
        match_option="INTERSECT",
    )
    return join_layer_path

def count_addresses(join_layer_path):
    # Count the number of addresses in the join layer
    count_result = arcpy.management.GetCount(join_layer_path)
    count = int(count_result.getOutput(0))
    print(f"The number of addresses that fall within the intersect layer is: {count}")
    return count

def add_to_project(new_layer_path):
    # Add the joined layer to the project
    proj_path = r"C:\Users\as425\Documents\GIS Programming\westnileoutbreak\WestNileOutbreak\WestNileOutbreak.aprx"
    aprx = arcpy.mp.ArcGISProject(proj_path)
    map_doc = aprx.listMaps()[0]

    map_doc.addDataFromPath(new_layer_path)
    print(f"Added {new_layer_path} to the project.")

    aprx.save()
    print("Project saved.")

# Main script execution
if __name__ == '__main__':
    setup()  # Initialize the setup

    # List of layers to process
    buffer_layer_list = ["Mosquito_Larval_Sites", "Wetlands", "Lakes_and_Reservoirs", "OSMP_Properties"]

    # Loop through each layer, request buffer distance, and perform the buffer operation
    for layer in buffer_layer_list:
        print(f"Processing layer: {layer}")

        # Request user input for buffer distance
        input_distance = input("Enter the buffer distance in feet: ")

        # Perform buffering
        buffer(layer, input_distance + " feet")
    print("Buffering complete.")

    # Perform intersection of buffered layers
    lyr_intersect_path = intersect([f"buf_{layer}" for layer in buffer_layer_list]) # Placeholder method call
    print("Intersect complete.")

    # Perform spatial join
    joined_layer_path = spatial_join("Building_Addresses", lyr_intersect_path)
    print("Spatial join complete.")

    # Count addresses within the intersect layer
    print("Counting addresses within the intersect layer...")
    address_count = count_addresses(joined_layer_path)
    print(f"Number of addresses within the intersect layer: {address_count}")

    # Add the joined feature class to the project
    add_to_project(joined_layer_path)
    print("All operations completed successfully.")