import subprocess
import os
import sys
import json
#from shapely import geometry as g

#from tqdm import tqdm

def find_POIs(lon, lat, dlon, dlat, poi_type="amenity", poi_type2="bench", verbose=False):
    lonlat = [lon, lat]
    lat1 = lonlat[1] - dlat
    lon1 = lonlat[0] - dlon
    lat2 = lonlat[1] + dlat
    lon2 = lonlat[0] + dlon

    query = """
    [out:json][timeout:25];
    // gather results
    (
    node["{0}"~"{1}"]({2},{3},{4},{5});
    way["{0}"~"{1}"]({2},{3},{4},{5});
    relation["{0}"~"{1}"]({2},{3},{4},{5});
            );
            // print results
            out body;
            >;
            out skel qt;""".format(poi_type, poi_type2, lat1,lon1,lat2,lon2)

    query_file = "query.osm"
    json_file = "result.json"
    if os.path.exists(json_file):
        os.remove(json_file)
    with open(query_file,"w") as f:
        f.write(query)

    # this gets the closest pitches in osm format
    cmd = "wget -O {} --post-file={} http://overpass-api.de/api/interpreter".format(json_file, query_file)
    # this uses the osmtogeojson utility to convert osm format to a geojson format which has coordinates (lon lats)
    subprocess.check_call(cmd.split(' '))
    cmd2 = "osmtogeojson -f json {}".format(json_file)
    gjson = subprocess.check_output(cmd2.split(' '))

    data = json.loads(gjson)
    result = []
    for i, feat in enumerate(data['features']):
        geom = feat['geometry']
        if geom['type'].lower()!="point":
            continue
        if poi_type2 == "toilets":
            props = feat["properties"]
            if "unisex" not in props or props["unisex"]=="no":
                continue
            #print props["unisex"]
            if "access" in props:
                access = props["access"]
            else:
                access = "unknown"
        coords = feat['geometry']['coordinates']
        lon = coords[0]
        lat = coords[1]
        if poi_type2 !="toilets":
            result.append((lon, lat))
        else:
            result.append((lon, lat, access))
    return result

if __name__ == '__main__':
    lon = 8
    dlon = 2.5
    lat = 46.5
    dlat = 1
    # contain entire switzerland pretty much
    toilets = find_POIs(lon, lat, dlon, dlat, "amenity", "toilets")
    #benches = find_POIs(lon, lat, dlon, dlat, "amenity", "bench")
    #benches = find_POIs(lon, lat, dlon, dlat, "amenity", "bench")
    #fountains = find_POIs(lon, lat, dlon, dlat, "amenity", "drinking_water")
    #with open("swiss-pois.csv", "w") as f:
    #    for lon, lat in benches:
    #        f.write("{},{},{}\n".format(lon, lat, "bench"))
    #    for lon, lat in fountains:
    #        f.write("{},{},{}\n".format(lon, lat, "drinking_water"))
    with open("swiss-toilets.csv", "w") as f:
        for lon, lat, access in toilets:
            f.write("{},{},{},{}\n".format(lon, lat, access,"unisex_toilet"))
