import sys
import folium
import os
import geopy
import pandas as pd
from folium.plugins import FloatImage
from geopy.geocoders import Nominatim, ArcGIS, GoogleV3  # Geocoder APIs
import psycopg2

# data from db
conn = psycopg2.connect(
    database="aprecisioncompanydb",
    user="postgres",
    password="infrastructure",
    host="127.0.0.1",
    port="5432",
)
conn.autocommit = True
cursor = conn.cursor()

# Create sorted list of id values to get most recent id for cursor.execute
cursor.execute("""SELECT id from docgen_docgen""")
i = cursor.fetchall()
n = 0  # Index variable
idList = []
for item in i:
    # Pull int values from lists
    idList.append(i[n][0])
    n += 1
print(idList[-1])
cursor.execute(
    f"""SELECT * from docgen_docgen WHERE id = {idList[-1]}"""
)  # Most recent entry only
result = cursor.fetchone()
conn.close()
rf = result[7]

userInFile = result[7]
userInFile = pd.read_csv(userInFile)
oidList = userInFile["No."].values.tolist()
lenList = userInFile["Length"].values.tolist()
widList = userInFile["Width"].values.tolist()
scList = userInFile["Special Case"].values.tolist()
qdList = userInFile["Quick Description"].values.tolist()
xList = userInFile["x"].values.tolist()
yList = userInFile["y"].values.tolist()

try:
    workOrderLoc = result[34]
except:
    workOrderLoc = "No"  # Keep default set to "no" when not testing
try:
    mapLayers = result[21]
except:  # ACCEPTABLE INPUT: "dnr", "repairs", "dnr and repair"
    mapLayers = "dnr and repair"
try:
    dnrPrice = result[18]
except:
    dnrPrice = 15
try:
    smPrice = result[31]
except:
    smPrice = 2.5
try:
    mdPrice = result[23]
except:
    mdPrice = 5
try:
    lgPrice = result[20]
except:
    lgPrice = 10
try:
    curbPrice = result[17]
except:
    curbPrice = 10

print(dnrPrice, smPrice, mdPrice, lgPrice, curbPrice)

# Define dicts for unique streets for each deficiency
uniqueStrNames_totH_count = {}
uniqueStrNames_sm_sqft = {}
uniqueStrNames_md_sqft = {}
uniqueStrNames_lg_sqft = {}
uniqueStrNames_curb_length = {}
uniqueStrNames_dnr_sqft = {}
uniqueStrNames_sm_cost = {}
uniqueStrNames_md_cost = {}
uniqueStrNames_lg_cost = {}
uniqueStrNames_curb_cost = {}
uniqueStrNames_dnr_cost = {}
uniqueStrNames_sm_count = {}
uniqueStrNames_md_count = {}
uniqueStrNames_lg_count = {}
uniqueStrNames_curb_count = {}
uniqueStrNames_dnr_count = {}

centerX = 0
centerY = 0
# Calculate center of map from averages of lats and longs

# Reverse Geocode instantiation
g = ArcGIS()
addresses = []

centerX = sum(xList) / (len(xList))
centerY = sum(yList) / (len(yList))
print(centerX, centerY)


def Map():
    coord = [centerX, centerY]
    # tiles = Stamen Toner, Stamen Terrain, Stamen Watercolor, OpenStreetMap (default)
    m = folium.Map(
        coord, zoom_start=15, tiles="OpenStreetMap", overlay=True, control=True
    )

    tile = folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        opacity=0.9,
        attr="Esri",
        name="Esri Satellite",
        overlay=True,
        control=True,
    ).add_to(m)

    tileRef = folium.TileLayer(
        tiles="https://basemaps.arcgis.com/arcgis/rest/services/World_Basemap_v2/VectorTileServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Esri Vector Tile Layer",
        overlay=True,
        control=True,
    ).add_to(m)

    marker = []
    hT = []
    overallType = []
    img1 = []
    img2 = []
    id = []
    deficiencyType = []
    sqft_or_curbLength = []

    print("stop here")

    i = 0
    while i < len(xList) - 1:
        # for item in xList:
        # if i > 1:

        x = xList[i]
        y = yList[i]
        marker.append(x)
        marker.append(y)

        objID = oidList[i]
        id.append(int(objID))

        # Add address data to list
        a = g.reverse((x, y), timeout=10)
        addresses.append(a)

        # add defiency type to list

        if qdList[i] == "Small" or qdList[i] == "Medium" or qdList[i] == "Large":
            deficiencyType.append(qdList[i])
        else:
            deficiencyType.append(scList[i])

        j = 0
        while j < len(xList) - 1:
            if scList[i] == "Replace":  # shape is square
                overallType.append("Replace")
            else:  # Shape is circle
                overallType.append("SpecialCond")
            j += 1

        if (
            scList[i] != "" and scList[i] != " "
        ):  # change "special condition" entries to square (dnr) or circles
            if scList[i] == "Curb":
                hazardType = "purple"
            elif scList[i] == "GutterPan":
                hazardType = "blue"
            elif scList[i] == "Replace":
                hazardType = "green"
            elif scList[i] == "Bottom HC":
                hazardType = "orange"
            elif scList[i] == "Curb to Brick":
                hazardType = "light red"
            elif scList[i] == "SW2C":
                hazardType = "white"
            # elif scList[i] == "Sidewalk to Curb":
            #   hazardType = "white"
            elif scList[i] == "Driveway":
                hazardType = "yellow"
            elif scList[i] == "Asphalt":
                hazardType = "black"
            elif scList[i] == "Leadwalk":
                hazardType = "gray"
            elif scList[i] == "Catch Basin":
                hazardType = "light green"
            elif scList[i] == "Quality":
                hazardType = "pink"
            elif scList[i] == "Other":
                hazardType = "dark gray"

        else:  # Shape is pin
            overallType.append("NormalRepair")
            if qdList[i] == "Small":
                hazardType = "yellow"
            if qdList[i] == "Medium":
                hazardType = "darkblue"
            if qdList[i] == "Large":
                hazardType = "red"

        hT.append((hazardType))
        i += 1
    print(addresses)

    # Create list of road names only from addresses list
    itemList = []
    newLineList = []
    nLL = []
    for item in addresses:
        itemList.append(str(item))
    for item in itemList:
        strippedItem = item.strip()
        ni = strippedItem.split(",")
        newLineList.append(ni[0])
    for item in newLineList:
        res = "".join([i for i in item if not i.isdigit()])
        nLL.append(res[1:])

    # Create dictionaries with unique road names for count, sqft, cost for all deficiency types
    # Total Hazard Count
    n = -1
    for item in nLL:
        if item not in uniqueStrNames_totH_count:
            uniqueStrNames_totH_count[item] = 0
    for item in nLL:
        n += 1
        if item in uniqueStrNames_totH_count:
            if deficiencyType[n] == "Small":
                uniqueStrNames_totH_count[item] += 1
    # small count
    n = -1
    for item in nLL:
        if item not in uniqueStrNames_sm_count:
            uniqueStrNames_sm_count[item] = 0
    for item in nLL:
        n += 1
        if item in uniqueStrNames_sm_count:
            if deficiencyType[n] == "Small":
                uniqueStrNames_sm_count[item] += 1
    # medium count
    n = -1
    for item in nLL:
        if item not in uniqueStrNames_md_count:
            uniqueStrNames_md_count[item] = 0
    for item in nLL:
        n += 1
        if item in uniqueStrNames_md_count:
            if deficiencyType[n] == "Medium":
                uniqueStrNames_md_count[item] += 1
    # large count
    n = -1
    for item in nLL:
        if item not in uniqueStrNames_lg_count:
            uniqueStrNames_lg_count[item] = 0
    for item in nLL:
        n += 1
        if item in uniqueStrNames_lg_count:
            if deficiencyType[n] == "Large":
                uniqueStrNames_lg_count[item] += 1
    # curb count
    n = -1
    for item in nLL:
        if item not in uniqueStrNames_curb_count:
            uniqueStrNames_curb_count[item] = 0
    for item in nLL:
        n += 1
        if item in uniqueStrNames_curb_count:
            if deficiencyType[n] == "Curb":
                uniqueStrNames_curb_count[item] += 1
    # dnr count
    n = -1
    for item in nLL:
        if item not in uniqueStrNames_dnr_count:
            uniqueStrNames_dnr_count[item] = 0
    for item in nLL:
        n += 1
        if item in uniqueStrNames_dnr_count:
            if deficiencyType[n] == "Replace":
                uniqueStrNames_dnr_count[item] += 1

    sqftList = []
    costList = []
    tempNum = 0
    for entry in qdList:
        if entry == "Small":
            sqftList.append(float(lenList[tempNum]) * float(widList[tempNum]))
            costList.append(float(sqftList[tempNum]) * float(smPrice))
            tempNum += 1
        elif entry == "Medium":
            sqftList.append(float(lenList[tempNum]) * float(widList[tempNum]))
            costList.append(float(sqftList[tempNum]) * float(mdPrice))
            tempNum += 1
        elif entry == "Large":
            sqftList.append(float(lenList[tempNum]) * float(widList[tempNum]))
            costList.append(float(sqftList[tempNum]) * float(lgPrice))
            tempNum += 1
        else:
            if scList[tempNum] == "Curb":
                sqftList.append(float(lenList[tempNum]))
                costList.append(float(sqftList[tempNum]) * float(curbPrice))
                tempNum += 1
            elif scList[tempNum] == "Replace":
                sqftList.append(float(lenList[tempNum]) * float(widList[tempNum]))
                costList.append(float(sqftList[tempNum]) * float(dnrPrice))
                tempNum += 1
            else:
                sqftList.append(0)
                costList.append(0)
                print("entry is not equal to sml, med, lg, dnr, or curb")
                tempNum += 1
    print(
        len(lenList),
        len(widList),
        len(qdList),
        len(scList),
        len(sqftList),
        len(costList),
    )

    # small sqft
    n = -1
    for item in nLL:
        if item not in uniqueStrNames_sm_sqft:
            uniqueStrNames_sm_sqft[item] = 0
    # medium sqft
    n = -1
    for item in nLL:
        if item not in uniqueStrNames_md_sqft:
            uniqueStrNames_md_sqft[item] = 0
    # large sqft
    n = -1
    for item in nLL:
        if item not in uniqueStrNames_lg_sqft:
            uniqueStrNames_lg_sqft[item] = 0
    # curb length
    n = -1
    for item in nLL:
        if item not in uniqueStrNames_curb_length:
            uniqueStrNames_curb_length[item] = 0
    # dnr sqft
    n = -1
    for item in nLL:
        if item not in uniqueStrNames_dnr_sqft:
            uniqueStrNames_dnr_sqft[item] = 0
    # small cost
    n = -1
    for item in nLL:
        if item not in uniqueStrNames_sm_cost:
            uniqueStrNames_sm_cost[item] = 0
    # medium cost
    n = -1
    for item in nLL:
        if item not in uniqueStrNames_md_cost:
            uniqueStrNames_md_cost[item] = 0
    # large cost
    n = -1
    for item in nLL:
        if item not in uniqueStrNames_lg_cost:
            uniqueStrNames_lg_cost[item] = 0
    # curb cost
    n = -1
    for item in nLL:
        if item not in uniqueStrNames_curb_cost:
            uniqueStrNames_curb_cost[item] = 0
    # dnr cost
    n = -1
    for item in nLL:
        if item not in uniqueStrNames_dnr_cost:
            uniqueStrNames_dnr_cost[item] = 0
    tn = 0
    for item in nLL:
        if qdList[tn] == "Small":
            uniqueStrNames_sm_sqft[item] += sqftList[tn]
            uniqueStrNames_sm_cost[item] += costList[tn]
            tn += 1
        elif qdList[tn] == "Medium":
            uniqueStrNames_md_sqft[item] += sqftList[tn]
            uniqueStrNames_md_cost[item] += costList[tn]
            tn += 1
        elif qdList[tn] == "Large":
            uniqueStrNames_lg_sqft[item] += sqftList[tn]
            uniqueStrNames_lg_cost[item] += costList[tn]
            tn += 1
        else:
            if scList[tn] == "Curb":
                uniqueStrNames_curb_length[item] += sqftList[tn]
                uniqueStrNames_curb_cost[item] += costList[tn]
            elif scList[tn] == "Replace":
                uniqueStrNames_dnr_sqft[item] += sqftList[tn]
                uniqueStrNames_dnr_cost[item] += costList[tn]
                tn += 1
            else:
                print("entry is not equal to sml, med, lg, dnr, or curb")
                tn += 1

    ###

    # Add markers to map
    # print(marker)
    i = 0
    j = 0
    # print(img1, img2)
    if workOrderLoc.lower() == "yes":
        while i < len(marker) - 1:
            folium.Marker(
                [float(marker[i]), float(marker[i + 1])],
                icon=folium.features.CustomIcon(
                    "https://jcleftwi.github.io/GIS715/pin.png", icon_size=(15, 16)
                ),
            ).add_to(m)
            # print(marker[i], marker[i + 1])
            i += 2
            j += 1
    else:
        while i < len(marker) - 1:
            if "dnr" in mapLayers.lower() and "repair" in mapLayers.lower():
                if overallType[j] == "NormalRepair":  # Normal hazard
                    if hT[j] == "yellow":
                        icon_path = r"https://jcleftwi.github.io/GIS715/yellowPin.png"
                        icon = folium.features.CustomIcon(
                            icon_image=icon_path, icon_size=(15, 16)
                        )
                        folium.Marker(
                            [float(marker[i]), float(marker[i + 1])],
                            popup=(
                                (id[j]),
                                (
                                    "<div style=width:300px ><img src="
                                    + "'"
                                    + img1[j]
                                    + "'"
                                    + "width=125px></div>"
                                ),
                                (
                                    "<div style=width:300px ><img src="
                                    + "'"
                                    + img2[j]
                                    + "'"
                                    + "width=125px></div>"
                                ),
                                (addresses[j]),
                            ),
                            icon=icon,
                        ).add_to(m)
                        # print(marker[i], marker[i + 1])
                        i += 2
                        j += 1
                    elif hT[j] == "darkblue":
                        icon_path = r"https://jcleftwi.github.io/GIS715/bluePin.png"
                        icon = folium.features.CustomIcon(
                            icon_image=icon_path, icon_size=(15, 16)
                        )
                        folium.Marker(
                            [float(marker[i]), float(marker[i + 1])],
                            popup=(
                                (id[j]),
                                (
                                    "<div style=width:300px ><img src="
                                    + "'"
                                    + img1[j]
                                    + "'"
                                    + "width=125px></div>"
                                ),
                                (
                                    "<div style=width:300px ><img src="
                                    + "'"
                                    + img2[j]
                                    + "'"
                                    + "width=125px></div>"
                                ),
                                (addresses[j]),
                            ),
                            icon=icon,
                        ).add_to(m)
                        # print(marker[i], marker[i + 1])
                        i += 2
                        j += 1
                    else:
                        icon_path = r"https://jcleftwi.github.io/GIS715/redPin.png"
                        icon = folium.features.CustomIcon(
                            icon_image=icon_path, icon_size=(15, 16)
                        )
                        folium.Marker(
                            [float(marker[i]), float(marker[i + 1])],
                            popup=(
                                (id[j]),
                                (
                                    "<div style=width:300px ><img src="
                                    + "'"
                                    + img1[j]
                                    + "'"
                                    + "width=125px></div>"
                                ),
                                (
                                    "<div style=width:300px ><img src="
                                    + "'"
                                    + img2[j]
                                    + "'"
                                    + "width=125px></div>"
                                ),
                                (addresses[j]),
                            ),
                            icon=icon,
                        ).add_to(m)
                        # print(marker[i], marker[i + 1])
                        i += 2
                        j += 1
                elif overallType[j] == "Replace":  # square - dnr
                    folium.RegularPolygonMarker(
                        [float(marker[i]), float(marker[i + 1])],
                        radius=6,
                        popup=(
                            (id[j]),
                            (
                                "<div style=width:300px ><img src="
                                + "'"
                                + img1[j]
                                + "'"
                                + "width=125px></div>"
                            ),
                            (
                                "<div style=width:300px ><img src="
                                + "'"
                                + img2[j]
                                + "'"
                                + "width=125px></div>"
                            ),
                            (addresses[j]),
                        ),
                        color=hT[j],
                        fill_color=hT[j],
                        icon="",
                        fill_opacity=1,
                    ).add_to(m)
                    # print(marker[i], marker[i + 1])
                    i += 2
                    j += 1
                else:  # Non-dnr special cond
                    folium.CircleMarker(
                        [float(marker[i]), float(marker[i + 1])],
                        popup=(
                            (id[j]),
                            (
                                "<div style=width:300px ><img src="
                                + "'"
                                + img1[j]
                                + "'"
                                + "width=125px></div>"
                            ),
                            (
                                "<div style=width:300px ><img src="
                                + "'"
                                + img2[j]
                                + "'"
                                + "width=125px></div>"
                            ),
                            (addresses[j]),
                        ),
                        radius=2.5,
                        color=hT[j],
                        fill_color=hT[j],
                        fill_opacity=1,
                    ).add_to(m)
                    # print(marker[i], marker[i + 1])
                    i += 2
                    j += 1
            elif "repair" not in mapLayers.lower():
                if overallType[j] == "Replace":
                    folium.RegularPolygonMarker(
                        [float(marker[i]), float(marker[i + 1])],
                        radius=6,
                        popup=(
                            (id[j]),
                            (
                                "<div style=width:300px ><img src="
                                + "'"
                                + img1[j]
                                + "'"
                                + "width=125px></div>"
                            ),
                            (
                                "<div style=width:300px ><img src="
                                + "'"
                                + img2[j]
                                + "'"
                                + "width=125px></div>"
                            ),
                            (addresses[j]),
                        ),
                        color=hT[j],
                        fill_color=hT[j],
                        icon="",
                        fill_opacity=1,
                    ).add_to(m)
                    # print(marker[i], marker[i + 1])
                    i += 2
                    j += 1
                else:
                    i += 2
                    j += 1
            else:
                if overallType[j] == "NormalRepair":  # Normal hazard
                    if hT[j] == "yellow":
                        icon_path = r"https://jcleftwi.github.io/GIS715/yellowPin.png"
                        icon = folium.features.CustomIcon(
                            icon_image=icon_path, icon_size=(15, 16)
                        )
                        folium.Marker(
                            [float(marker[i]), float(marker[i + 1])],
                            popup=(
                                (id[j]),
                                (
                                    "<div style=width:300px ><img src="
                                    + "'"
                                    + img1[j]
                                    + "'"
                                    + "width=125px></div>"
                                ),
                                (
                                    "<div style=width:300px ><img src="
                                    + "'"
                                    + img2[j]
                                    + "'"
                                    + "width=125px></div>"
                                ),
                                (addresses[j]),
                            ),
                            icon=icon,
                        ).add_to(m)
                        # print(marker[i], marker[i + 1])
                        i += 2
                        j += 1
                    elif hT[j] == "darkblue":
                        icon_path = r"https://jcleftwi.github.io/GIS715/bluePin.png"
                        icon = folium.features.CustomIcon(
                            icon_image=icon_path, icon_size=(15, 16)
                        )
                        folium.Marker(
                            [float(marker[i]), float(marker[i + 1])],
                            popup=(
                                (id[j]),
                                (
                                    "<div style=width:300px ><img src="
                                    + "'"
                                    + img1[j]
                                    + "'"
                                    + "width=125px></div>"
                                ),
                                (
                                    "<div style=width:300px ><img src="
                                    + "'"
                                    + img2[j]
                                    + "'"
                                    + "width=125px></div>"
                                ),
                                (addresses[j]),
                            ),
                            icon=icon,
                        ).add_to(m)
                        # print(marker[i], marker[i + 1])
                        i += 2
                        j += 1
                    else:
                        icon_path = r"https://jcleftwi.github.io/GIS715/redPin.png"
                        icon = folium.features.CustomIcon(
                            icon_image=icon_path, icon_size=(15, 16)
                        )
                        folium.Marker(
                            [float(marker[i]), float(marker[i + 1])],
                            popup=(
                                (id[j]),
                                (
                                    "<div style=width:300px ><img src="
                                    + "'"
                                    + img1[j]
                                    + "'"
                                    + "width=125px></div>"
                                ),
                                (
                                    "<div style=width:300px ><img src="
                                    + "'"
                                    + img2[j]
                                    + "'"
                                    + "width=125px></div>"
                                ),
                                (addresses[j]),
                            ),
                            icon=icon,
                        ).add_to(m)
                        # print(marker[i], marker[i + 1])
                        i += 2
                        j += 1

                elif overallType[j] == "Replace":
                    i += 2
                    j += 1
                else:  # Non-dnr special cond
                    folium.CircleMarker(
                        [float(marker[i]), float(marker[i + 1])],
                        popup=(
                            (id[j]),
                            (
                                "<div style=width:300px ><img src="
                                + "'"
                                + img1[j]
                                + "'"
                                + "width=125px></div>"
                            ),
                            (
                                "<div style=width:300px ><img src="
                                + "'"
                                + img2[j]
                                + "'"
                                + "width=125px></div>"
                            ),
                            (addresses[j]),
                        ),
                        radius=6,
                        color=hT[j],
                        fill_color=hT[j],
                        fill_opacity=1,
                    ).add_to(m)
                    print(marker[i], marker[i + 1])
                    i += 2
                    j += 1

    folium.LayerControl().add_to(m)
    m.save("index.html")


m = Map()
