---
layout: datavis
title: Earthquakes in Chile
---

<div id="map"></div>
<div id="d3layer" class="d3-vec"></div>

<script src="../js/d3.v2.js"></script>
<script src='http://api.tiles.mapbox.com/mapbox.js/v0.6.6/mapbox.js'></script>
<script type="text/javascript">

  var MS_BY_DAY = 24 * 60 * 60 * 1000,
      data = {};

  function epochDay(datetime) {
    var epochms = Date.parse(datetime);
    return (epochms - epochms % MS_BY_DAY) / MS_BY_DAY;
  }

  function addEarthquakeMetadata(featureCollection) {

    var pointFeatures = featureCollection.features,
        firstItem = pointFeatures[0],
        offsetDay = Math.abs(epochDay(firstItem.properties.datetime));

    pointFeatures.forEach(function(item) {
      var date = new Date(item.properties.datetime);
      item.properties["day"] = epochDay(item.properties.datetime) + offsetDay;
      item.properties["year"] = date.getFullYear();
    });
  }

  d3.json("../data/full.json", function(featureCollection) {
    
    // Visualization variables
    var div,
        svg,
        grp,
        txtYear,
        txtPlay;

    // Visualization setup
    div = d3.select("#d3layer"),
    svg = div.append("svg"),
    grp = svg.append("g");

    txtYear = svg.append("text")
      .text("1900")
      .attr("x",  30)
      .attr("y", 100)
      .attr("class", "year")
      .attr("font-size", "50"),
    txtPlay = svg.append("text")
      .text("PLAY ▶")
      .attr("x", 30)
      .attr("y", 130)
      .attr("class", "playout");

    addEarthquakeMetadata(featureCollection);
    
    var pointFeatures = featureCollection.features,
        numPoints = pointFeatures.length,
        totalDuration = 60 * 1000,
        lastDay = pointFeatures[numPoints - 1].properties.day,
        dayDuration = Math.floor(totalDuration / lastDay);

    function setup_svg(width, height) {
      svg.attr("width", width)
        .attr("height", height)
        .style("margin-left", "0px")
        .style("margin-top",  "0px");
    }

    function d3layer() {

      var layer = {},
        bounds,
        feature,
        collection,
        first = true;
        
      layer.parent = div.node();

      layer.project = function(x) {
        var point = layer.map.locationPoint({ lat: x[1], lon: x[0] });
        return [point.x, point.y];
      }

      layer.draw_earthquakes = function() {

        path = d3.geo.path()
            .projection(layer.project)
            .pointRadius(0);

        feature.attr("d", path);                   

        path = d3.geo.path()
          .projection(layer.project)
          .pointRadius(function(d) {
            return 1 + Math.floor(0.4 * Math.pow(2, d.properties.magnitude));
          });

        feature.transition()
          .delay(function(d) {
            return d.properties.day;
          })
          .duration(function(d) { 
            return Math.floor(100 * d.properties.magnitude);
          })
          .each("start", function() {
            txtYear.text(this.__data__.properties.year)
              .attr("font-size", "50");
            d3.select(this).attr("class", "eqpoint")
              .attr("fill-opacity", 0.2);
          })
          .each("end", function() {
            d3.select(this).attr("fill-opacity", 0.0);
          })
          .attr("d", path)
          .remove();
      }

      layer.draw = function() {

        if (first) {
          setup_svg(layer.map.dimensions.x, layer.map.dimensions.y);
          txtPlay.on("click", layer.draw_earthquakes)
            .on("mouseover", function() {
              txtPlay.attr("class", "playover");
            })
            .on("mouseout", function() {
              txtPlay.attr("class", "playout");
            });
          first = false;
        }

      };

      layer.data = function(x) {

          collection = x;
          bounds = d3.geo.bounds(collection);
          feature = grp.selectAll("path")
            .data(collection.features)
            .enter()
            .append("path")
            .attr("class", "eqpoint");
    
          return layer;
        };

        layer.extent = function() {
          return new MM.Extent(
            new MM.Location(bounds[0][1], bounds[0][0]),
            new MM.Location(bounds[1][1], bounds[1][0]));
        };

        return layer;
      };

    var map,
        earthquakeLayer;

    mapbox.load('pnavarrc.map-me21qrt6', function(o) {

      earthquakeLayer = d3layer().data(featureCollection);
      map = mapbox.map("map", o.layer, null, []);
      map.setExtent([
        {lat:  15.00, lon: -30.00},
        {lat: -55.00, lon: -85.00}
      ]);
      map.zoom(3);
      map.ui.attribution.add()
      .content('<a href="http://mapbox.com/about/maps">Terms &amp; Feedback</a>');
                
      map.addLayer(earthquakeLayer);
    });
  });
</script>


