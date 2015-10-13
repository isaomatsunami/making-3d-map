Making 3D Map with GDAL/QGIS/webGL
=======================================

On May 3, 2015, Japan's Meteorological Agency issued the volcanic alert for Hakone, most popular destination for foreign tourists, restricting access to the area 300 meters from Owakudani. 

The agency's press release was like this.

![press release 20150503](images/hakone20150503.png)

Obviously, they have depth data.

I found researchers' network, JMA Unified Hypocenter Catalogs <https://hinetwww11.bosai.go.jp/auth/?LANG=en> , asked for a user account and permission to use data.

------------------------
Elevation data
------------------------

Terrain data is called DEM, digital elevation model. DEM is a collection of representative height of each latitude/longitude grid cell.

In Japan, Geospatial Information Authority(GSI) publishes 10 meter mesh of DEM for whole country and 5 meter mesh for volcanic area. In this page, I use Aster Global DEM, 30 meter mesh for whole globe, maintained by NASA amd Japan's METI. 

In Earth Explorer: <http://earthexplorer.usgs.gov>, select ASTER GLOBAL DEM as dataset and download 2 files which seem to cover Hakone area.

![earth explorer aster DEM](images/earth_explorer_asterGDEM.png)

Check 2 DEM files by dropping onto QGIS.

![aster DEM on QGIS](images/ASTER_QGIS.png)

#### Be conscious of SRS/CRS (spatial/coordinate reference system)

> SRS/CRS is DATUM + PROJECTION.
> DATUM is an assumption about the Earth (radius, flattening, meridian). WGS 84 meridian of zero longitude is NOT the Greenwich meridian (the prime meridian passes 100m east of the Royal Observatory). Presumed earth radius differs from time to time. Japan revised SRS after 2011 earthquake due to 5-meter landslide in the eastern Japan. France has had their own prime meridian.
> PROJECTION is a systematic transformation of lon/lat onto the plane (Mercator/Lambert/Albers, and where is the center of the map). Mercator projection is one of the most famous ones. Google Maps uses Google Mercator.
> Map data with SRS is called **geo-referenced**. Geotif image is tif image with SRS embedded in the header of the file. Shapefile(.shp) is often accompanied with projection file(.prj).
> Geo-referenced data can be processed with GDAL/OGR library. For example, a Geotif image can be transformed from one SRS to another SRS image by using gdal_warp command.


You can easily, by QGIS, merge files into a single file and clip area as you want. In this page, I use GDAL/OGR directly from command line. (because I want to clip data exactly)

What I want is:

* Owakudani (lon,lat) = (139.027287, 35.245254)
* clip area [northwest, southeast] = [(138.9,35.35), (139.1,35.15)]

Merge 2 files and clip target area from console.

```
	$ gdal_merge.py \
		-of GTiff \
		-o hakoneDEM.tif \
		ASTGTM2_N35E138/ASTGTM2_N35E138_dem.tif \
		ASTGTM2_N35E139/ASTGTM2_N35E139_dem.tif
	$ gdal_translate \
		-projwin 138.9 35.35 139.1 35.15 \
		-of GTiff \
		hakoneDEM.tif \
		owakudaniDEM.tif
```

Check by gdalinfo instead of QGIS this time.

```
	$ gdalinfo owakudaniDEM.tif
	Driver: GTiff/GeoTIFF
	Files: owakudaniDEM.tif
	Size is 720, 720
	Coordinate System is:
	GEOGCS["WGS 84",
	    DATUM["WGS_1984",
	        SPHEROID["WGS 84",6378137,298.257223563,
	            AUTHORITY["EPSG","7030"]],
	        AUTHORITY["EPSG","6326"]],
	    PRIMEM["Greenwich",0],
	    UNIT["degree",0.0174532925199433],
	    AUTHORITY["EPSG","4326"]]
	Origin = (138.899861111111107,35.350138888888893)
	Pixel Size = (0.000277777777778,-0.000277777777778)
	Metadata:
	  AREA_OR_POINT=Area
	Image Structure Metadata:
	  INTERLEAVE=BAND
	Corner Coordinates:
	Upper Left  ( 138.8998611,  35.3501389) (138d53'59.50"E, 35d21' 0.50"N)
	Lower Left  ( 138.8998611,  35.1501389) (138d53'59.50"E, 35d 9' 0.50"N)
	Upper Right ( 139.0998611,  35.3501389) (139d 5'59.50"E, 35d21' 0.50"N)
	Lower Right ( 139.0998611,  35.1501389) (139d 5'59.50"E, 35d 9' 0.50"N)
	Center      ( 138.9998611,  35.2501389) (138d59'59.50"E, 35d15' 0.50"N)
	Band 1 Block=720x5 Type=Int16, ColorInterp=Gray
```

Do you notice that clipped area is a little different from intention? Clipped data can be bigger than instructed.

Metadata:AREA_OR_POINT=Area means height data is representative height of each cell(that is pixel) in the grid. But I use this as point data so as to simplify mesh construction.

call my private function (in hakone directory) to get binary height-only data.

```
	python dem2npy.py owakudaniDEM.tif
```

owakudaniDEM.npy is multipled by 10 by dem2npy.py; Its first value is Upper Left, second is 1 pixel east of the first. You should check it by a binary editor and QGIS.


------------------------
Texture from Landsat
------------------------

Texture is a surface image of 3D graphics. In this page I use Landsat 8 data and CREATE an image.

![earth explorer landsat 8](images/earth_explorer_landsat8.png)

Find and download Level-1 production of cloudless image. In this case, LC81070362015122LGN00.tar

Level-1 production is composed of B1~B11 geoTiff files and BQA/MTL files.
Visible lights are Band2(blue), Band3(green) and Band4(red). Band8 is panchromatic(colorless), having 15 meter resolution. 

![landsat 8](images/landsat8.png)

Pansharpening is an operation which color-paints panchromatic image with less precise RGB images. There are several ways.

* arcGIS (easiest but expensive)
* gdal_pansharpen (wait for GDAL 2.1)
* GRASS GIS 7 (see http://planet.qgis.org/planet/tag/landsat/)
* write program (PanSharpening in hakone directory, this is not c++ source, if you want, e-mail me)

```
	# write out geometric information (tfw world file)
	# you can skip this
	listgeo -tfw LC81070362015122LGN00/LC81070362015122LGN00_B8.TIF

	./PanSharpening \
		--r LC81070362015122LGN00/LC81070362015122LGN00_B4.TIF \
		--g LC81070362015122LGN00/LC81070362015122LGN00_B3.TIF \
		--b LC81070362015122LGN00/LC81070362015122LGN00_B2.TIF \
		--pan LC81070362015122LGN00/LC81070362015122LGN00_B8.TIF \
		--weight 0.52 0.23 0.35 \
		--o LC81070362015122LGN00/LC81070362015122LGN00_PAN_NOINFO.TIF

	# this pansharpned image has no geometric information (not geo-referenced)
	# rebind B8 geoinfo to newly-created image
	geotifcp -e LC81070362015122LGN00/LC81070362015122LGN00_B8.TIF \
		LC81070362015122LGN00/LC81070362015122LGN00_PAN_NOINFO.TIF \
		LC81070362015122LGN00/LC81070362015122LGN00_PAN.TIF

	# clip the same area as DEM file
	$ gdal_translate \
		-projwin 138.9 35.35 139.1 35.15 \
		-of GTiff \
		LC81070362015122LGN00/LC81070362015122LGN00_PAN.TIF \
		owakudaniRGB.tif
	# this causes error. Projection is different. Check it.

	$ gdalinfo LC81070362015122LGN00/LC81070362015122LGN00_PAN.TIF
	Driver: GTiff/GeoTIFF
	Files: LC81070362015122LGN00/LC81070362015122LGN00_PAN.TIF
	Size is 15501, 15821
	Coordinate System is:
	PROJCS["WGS 84 / UTM zone 54N",
		GEOGCS["WGS 84",
			DATUM["WGS_1984",
    	        SPHEROID["WGS 84",6378137,298.257223563,
    	            AUTHORITY["EPSG","7030"]],
    	        AUTHORITY["EPSG","6326"]],
    	    PRIMEM["Greenwich",0],
	        UNIT["degree",0.0174532925199433],
	        AUTHORITY["EPSG","4326"]],
	    PROJECTION["Transverse_Mercator"],
	    PARAMETER["latitude_of_origin",0],
	    PARAMETER["central_meridian",141],
	    PARAMETER["scale_factor",0.9996],
	    PARAMETER["false_easting",500000],
	    PARAMETER["false_northing",0],
	    UNIT["metre",1,
	        AUTHORITY["EPSG","9001"]],
	    AUTHORITY["EPSG","32654"]]
	Origin = (261892.500000000000000,3948907.500000000000000)
	Pixel Size = (15.000000000000000,-15.000000000000000)
	Metadata:
	  AREA_OR_POINT=Area
	Image Structure Metadata:
	  INTERLEAVE=PIXEL
	Corner Coordinates:
	Upper Left  (  261892.500, 3948907.500) (138d22'11.30"E, 35d39'19.18"N)
	Lower Left  (  261892.500, 3711592.500) (138d26'10.92"E, 33d31' 2.69"N)
	Upper Right (  494407.500, 3948907.500) (140d56'17.50"E, 35d41' 2.57"N)
	Lower Right (  494407.500, 3711592.500) (140d56'23.14"E, 33d32'38.19"N)
	Center      (  378150.000, 3830250.000) (139d40'15.78"E, 34d36'24.72"N)
	Band 1 Block=15501x1 Type=UInt16, ColorInterp=Gray
	Band 2 Block=15501x1 Type=UInt16, ColorInterp=Undefined
	Band 3 Block=15501x1 Type=UInt16, ColorInterp=Undefined

	# EPSG is 32654, not 4326(=WGS84) of DEM file. So change it to 4326 (You can do it by QGIS)
	$ gdalwarp -overwrite \
	   -s_srs EPSG:32654 \
	   -t_srs EPSG:4326 \
	   -r cubic \
	   -of GTiff \
	   LC81070362015122LGN00/LC81070362015122LGN00_PAN.TIF \
	   LC81070362015122LGN00/LC81070362015122LGN00_PAN_4326.TIF

	# Now that you can safely clip the image
	$ gdal_translate -projwin 138.9 35.35 139.1 35.15 \
	   -of GTiff \
	   LC81070362015122LGN00/LC81070362015122LGN00_PAN_4326.TIF \
	   owakudaniRGB.tif

	# check again
	$ gdalinfo owakudaniRGB.tif
	Driver: GTiff/GeoTIFF
	Files: owakudaniRGB.tif
	Size is 1332, 1332
	Coordinate System is:
	GEOGCS["WGS 84",
	    DATUM["WGS_1984",
	        SPHEROID["WGS 84",6378137,298.257223563,
	            AUTHORITY["EPSG","7030"]],
	        AUTHORITY["EPSG","6326"]],
	    PRIMEM["Greenwich",0],
	    UNIT["degree",0.0174532925199433],
	    AUTHORITY["EPSG","4326"]]
	Origin = (138.899891210746461,35.350078925110978)
	Pixel Size = (0.000150166188241,-0.000150166188241)
	Metadata:
	  AREA_OR_POINT=Area
	Image Structure Metadata:
	  INTERLEAVE=PIXEL
	Corner Coordinates:
	Upper Left  ( 138.8998912,  35.3500789) (138d53'59.61"E, 35d21' 0.28"N)
	Lower Left  ( 138.8998912,  35.1500576) (138d53'59.61"E, 35d 9' 0.21"N)
	Upper Right ( 139.0999126,  35.3500789) (139d 5'59.69"E, 35d21' 0.28"N)
	Lower Right ( 139.0999126,  35.1500576) (139d 5'59.69"E, 35d 9' 0.21"N)
	Center      ( 138.9999019,  35.2500682) (138d59'59.65"E, 35d15' 0.25"N)
	Band 1 Block=1332x1 Type=UInt16, ColorInterp=Gray
	Band 2 Block=1332x1 Type=UInt16, ColorInterp=Undefined
	Band 3 Block=1332x1 Type=UInt16, ColorInterp=Undefined
```

![pansharpened](images/pansharpened.png)

owakudaniRGB.tif is 3-band geotiff image, not RGB image. If you open it by usual image softwares, it shows only the first band of the three, in black and white.

When you open it by QGIS, it automatically merges 3 band into RGB color image.
Click on the Layer and **save as image**, not as value. This image is still geo-referenced. 

![save as image](images/saveasimage.png)

Use your Photoshop as you want. But once you edit non-GIS editor, the image will lose geometric information.
**SO keep in mind** this geoinfo-less image, unless you trim/clip it, represents [(138.8998912,35.3500789), (139.0999126,35.1500576)] area even after it is resized. (You will have to resize it as webGL accept only power of two size such as 512, 1024, 2048....)

![photoshop map](images/photoshopmap.png)

------------------------
Quake data
------------------------

Next morning, I got my account and permission to use data from JMA Unified Hypocenter Catalogs.

The data looked like this.

![original quake data](images/originaldata.jpg)

What I filtered is this. 

![trimmed quake data](images/trimmeddata.png)

This is a good training for text manipulation by scripting languages (Python/Ruby).

------------------------
webGL presentation
------------------------

THREE.js is the most popular library and I used it for the first version of Hakone 3D map. But it is too large a library(THREE.min.js = 470KB), in many cases larger than geometry data. I wrote my own wrapper library. I won't elaborate how to use it.

Following points are common in both cases. 

#### LonLatAlt2XYZ function

DEM data and Quake data are longitude/latitude/altitude data. You need to translate it into X/Y/Z data. ECEF(Earth-Centered, Earth-Fixed) Cartesian coordinate system is the best target coordinate.

ECEF system: <https://en.wikipedia.org/wiki/ECEF>

In this case, I adopt a much simpler translation. 

Remember that the length of 1 degree of latitude is about 111000 meters. but that of longitude depends on latitude. At Owakudani (139.027287, 35.245254), 1 degree of longitude is about 90163 meters.
The function below, geoTranslator, returns function which translates (lon(deg),lat(deg),alt(km)) into [x,y,z] array.
(Are you familiar to closure in javascript?)


```javascript
    geoTranslator = function(offset_x,offset_y,offset_z,scale_x,scale_y,scale_z){
        function fX(x,y,z){return (x - offset_x) * scale_x;};
        function fY(x,y,z){return (y - offset_y) * scale_y;};
        function fZ(x,y,z){return (z - offset_z) * scale_z;};
        var geoTranslator = function(lon,lat,alt){
            return [fX(lon,lat,alt),fY(lon,lat,alt),fZ(lon,lat,alt)];
        };
        geoTranslator.inverse = function(_x, _y, _z){
            return [_x / scale_x + offset_x, _y / scale_y + offset_y, _z / scale_z + offset_z];
        };
        return geoTranslator;
    };
    var geo2xyz = geoTranslator(139.027287, 35.245254, 0, 90163 * 0.001, 110000 * 0.001, 0.001);

    # test
    console.log( geo2xyz(139,35,-0.5) );
```

By the same token, the function, uvTranslator, returns function which translates [lon(deg),lat(deg)] into [u,v]. This is used for calculation of uv texture coordinate. 

```javascript
    uvTranslator = function(top,right,left,bottom){
        var w = right - left, h = bottom - top;
        var bClamp = true;
        var uvTranslator = function(x,y){
            var u = (x - left) / w, v = (bottom - y) / h;
            if(bClamp){
                u = (u > 1.0) ? 1.0 : (u < 0.0) ? 0.0 : u;
                v = (v > 1.0) ? 1.0 : (v < 0.0) ? 0.0 : v;
            }
            return [u,v];
        };
        uvTranslator.clamp = function(b){
            bClamp = b;
        }
        return uvTranslator;
    };
    var geo2uv = uvTranslator(35.3500789, 139.0999126, 138.8998912, 35.1500576);

    # test
    console.log( geo2uv(139,35) );
```

**Recall** the texture image represents [(138.8998912,35.3500789), (139.0999126,35.1500576)].

#### Terrain geometry

After having loaded owakudaniDEM.npy, you have to construct terrain geometry.
You had inspected owakudaniDEM.tif before and gotten these information.
::

	$ gdalinfo owakudaniDEM.tif
	Driver: GTiff/GeoTIFF
	Files: owakudaniDEM.tif
	Size is 720, 720
	....
	Origin = (138.899861111111107,35.350138888888893)
	Pixel Size = (0.000277777777778,-0.000277777777778)

![geotiff coordinates](images/geotiffcoordinates.png)

Recall that owakudaniDEM.npy was a binary data of int16 and height value was multipled by 10.

```javascript
    # _dem is int16 binary data. change it to TypedArray
    var dem = new Int16Array(_dem);
    # containers and index
    var dem_3d = [], uv_dem = [], index = 0;
    
    # nLat, nLon are size of data
    var nLat = 720, nLon = 720;

    for (var i = 0;i < nLat;++i){
        for (var j = 0;j < nLon;++j){
            var lat = 35.350138888888893 + (i + 0.5) * -0.000277777777778;
            var lon = 138.899861111111107 + (j + 0.5) * 0.000277777777778;
            var alt = dem[index] * 0.1;
            dem_3d.push( geo2xyz( lon, lat, alt ) );
            uv_dem.push( geo2uv( lon, lat, alt ) );
            ++index;
        }
    }
    # Then construct webGL geometry by dem_3d, uv_dem
```

The webGL is another topic. Read the source code of sample_THREE.html, a minimum THREE.js sample.

![hakone sample](images/hakonesample.png)

-------------------------------
Geometry data compression
-------------------------------

![mesh data size](images/dataSizeOfMesh.jpg)

------------------------
Data size calculation
------------------------

Sending geometry data can be costly when it comes to large area. If a DEM geotiff size is 3000 * 3000, it will be 3000*3000*2(16bit) = 16MB. (Keep in mind that you will create equal-sized 2999*2999*2 = 18 millions triangles)

![ontake texture](images/ontake_texture.png)

When only small parts of the geotiff is of importance and the other part is just a background, Creating a triangle mesh, of which the area in focus is fine-meshed and other area sparsely meshed, can be more efficient.

But in this case, you have to send three (lon,lat,alt) data per triangle. Even if you reduce triangles to 1 million, you still have to send 1000000*3(vertices)*10( 32bit lon + 32bit lat + 16bit alt ) = 30MB data. 

[In this grapchis](http://www.tokyo-np.co.jp/hold/2014/ontake/one_month_ontake_eruption.html), Mesh around the top of the moutain is 10 meter resolution, background mountains are 500 meter mesh. Each of (lon,lat,alt) are quantized to 16bit*3 and a triangle is represented by 8bit*3 indices to shared vertices. The whole geometry data is reduced to below 1 MB.

![ontake mesh](images/ontake_mesh.png)

------------------------
Effects on readers
------------------------

When this map was published, quake data for recent 7 days was enough to show unusual change in the underground. I created 7 buttons to select date.

As volcanic activity lingered on, more buttons were needed. I changed UI to previous/next buttons. One month later, I created a d3.brush interface to select the range of data.

The alert by the administrative authority had huge impact on Hakone town, which heavily depends on tourism. The Meteorological Agency came under fierce criticism from local governments which urged quick lift of warning. On the other hand, access restriction for a very limited area caused wide suspicion that the agency were, for economic reasons,  underestimating risk.

This interactive 3D map allows readers to see underground activities temporally and spatially. Although non-experts can not make an assessment of the risk for themselves, they can understand the seismologists in the administration, who had raised the alert, have what kind of information, how precise data are.

I hope his approach of risk reporting is accepted in Japan, society that lost credibility on government and mass media after Fukushima nuclear disaster.

------------------------
Another example
------------------------

I wanted a texture image as a map for this 3D graphics.
![hong kong air traffic](images/HK_traffic.png)

If you have a shapefile of coastal line or land polygon, use shp2png.py (change parameters in the code)
![kanto area](images/kanto_area.png)

If not, one way to make image is binarization of satellite image.
Counter-intuitively, A blue image(Band 2) is not appropriate, forest is not distinguishable from see.
Near-infrared red image(Band 5) shows clearly coastal line.

![band image of landsat8](images/landsat_band.jpg)

Open Raster Calculator, set formula like **("LC81220452015003LGN00_B5@1" \< 6700) × 255 **. 

![raster calculator of band 5](images/qgis_raster_calc.png)

You will get binarized image.

![binary image of Band 5](images/BinaryB5.png)

------------------------
resource to learn
------------------------

* QGIS manual/training: <https://docs.qgis.org/2.8/en/docs/index.html>
* GDAL   <http://www.gdal.org>