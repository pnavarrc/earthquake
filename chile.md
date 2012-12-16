---
title: Earthquake Map
layout: mapvis
---

<script src="../js/d3.v2.js"></script>
<script type="text/javascript">

  var mapconf = {
      extent: [
	    {lat: -10.00, lon:  -70.00},
        {lat: -60.00, lon: -100.00}
  	  ],
      zoom: 4,
      mapid: "pnavarrc.map-me21qrt6"
  	},
    visconf = {
      duration: 2 * 60 * 1000, // Milliseconds
   	  radExp: 5,
   	  radExtent: [20, 300],
   	  durationEntent: [300, 1000]
   	};

  var magExtent, dayExtent;

  // Visualization setup
  var visDiv = d3.select('#d3l'),
   	  visSvg = visDiv.append('svg')
   	  visGrp = visSvg.append('g');

  // D3 Visualization Layer
  function D3Layer() {

    var layer = {},
   	  	bounds,
   	  	feature,
   	  	collection,
   	  	firstDraw = true;

   	layer.parent = visDiv.node();

   	layer.project = function(coord) {
   	  var svgPoint = layer.map.locationPoint({ lat: coord[1], lon: coord[0] });
   	  return [svgPoint.x, svgPoint.y];
   	};

   	layer.draw = function() {

   	  if (firstDraw) {

   	  	var btnPlay = d3.select('#btnPlay')
   	  		.on('click', layer.drawPoints);

   	  	visSvg.attr('width',  layer.map.dimensions.x)
   	  	      .attr('height', layer.map.dimensions.y);

   	  	firstDraw = false;
   	  }
   	};

	layer.drawPoints = function() {

	  var eqRadius = d3.scale.pow()
	  	    .domain(magExtent)
	  	    .rangeRound(visconf.radExtent)
	  	    .exponent(visconf.radExp),
	  	  eqDelay = d3.scale.linear()
	  	  	.domain(dayExtent)
	  	  	.rangeRound([0, visconf.duration]),
	  	  eqDuration = d3.scale.linear()
	  	  	.domain(magExtent)
	  	  	.range(visconf.durationEntent);

   	  path = d3.geo.path()
        .projection(layer.project)
        .pointRadius(0);

      feature.attr("d", path);

   	  path = d3.geo.path()
        .projection(layer.project)
        .pointRadius(function(item) { 
        	return eqRadius(item.properties.magnitude); 
        });
        
      feature.transition()
        .delay(function(item) {
          return eqDelay(item.properties.day);
        })
        .duration(function(item) {
        	return eqDuration(item.properties.magnitude);
        })
        .each('start', function() {
          d3.select(this).attr('fill-opacity', 0.2);	
        })
        .each('end', function() {
          d3.select(this).attr("fill-opacity", 0.0);
        })
        .attr('d', path);

   	};

   	layer.data = function(x) {
   	  collection = x,
   	  bounds = d3.geo.bounds(collection),
   	  feature = visGrp.selectAll('path')
   	    .data(collection.features)
   	    .enter()
   	  	.append('path')
   	  	.attr('class', 'eqpoint');

   	  return layer;
   	};

   	layer.extent = function() {
      return new MM.Extent(
        new MM.Location(bounds[0][1], bounds[0][0]),
        new MM.Location(bounds[1][1], bounds[1][0]));
    };

  	return layer;
  
  };

	function epochDay(datetime) {
	  var MS_DAY = 24 * 60 * 60 * 1000,
          ms_epoch = Date.parse(datetime);
      return (ms_epoch - ms_epoch % MS_DAY) / MS_DAY;
    };

  	// Load the data
   	d3.json('../data/full.json', function(earthquakeData) {

   	  // Add additional data to the eartquake events
      var earthquakePoints = earthquakeData.features, 
          firstDate = earthquakePoints[0].properties.datetime,
          dayOffset = Math.abs(epochDay(firstDate));

      earthquakePoints.forEach(function(item) {
      	var datetime = new Date(item.properties.datetime);
      	item.properties['day'] = epochDay(datetime) + dayOffset;
      	item.properties['year'] = datetime.getFullYear();
      });

	  magExtent = d3.extent(earthquakePoints, function(item) {
      	    return item.properties.magnitude;
          }),
      	  dayExtent = d3.extent(earthquakePoints, function(item) {
      	  	return item.properties.day;
      	  });


  	  // Load and draw the map
  	  mapbox.load(mapconf.mapid, function(mbmap) {

        map = mapbox.map("map", mbmap.layer);
        earthquakeLayer = D3Layer().data(earthquakeData);
		map.addLayer(earthquakeLayer);

        // Configure the inital state of the map
        map.setExtent(mapconf.extent);
        map.zoom(mapconf.zoom);
        map.ui.zoomer.add();
        map.ui.attribution.add()
          .content('<a href="http://mapbox.com/about/maps">Terms &amp; Feedback</a>');        
	  });

    });


</script>