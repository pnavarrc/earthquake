---
title: Earthquakes in Chile since 1900
layout: mapvis
---

<script src="/earthquake/js/d3.v2.min.js"></script>
<script type="text/javascript">

  var mapconf = {
      extent: [
	      {lat: -10.00, lon: -45.00},
        {lat: -60.00, lon: -75.00}
  	  ],
      zoom: 4,
      mapid: "pnavarrc.earthquakemap"
  	},
    visconf = {
      duration: 2 * 60 * 1000,
   	  radExp: 5,
   	  radExtent: [20, 300],
   	  durationEntent: [300, 1000],
   	  infoBox: {
   	  	width:  200,
   	  	height: 100,
   	  	margin: 40
   	  },
   	  txtInfo: {
   	  	margin: {
          top: 80, 
          left: 0
        },
   	  	fontsize: 50
   	  },
   	  colorExtent: [
   	  	d3.rgb('#fce94f'),
   	  	d3.rgb('#cc0001')
   	  ]
   	};

  var 

  // Visualization setup
  var visDiv = d3.select('#d3l'),
   	  visSvg = visDiv.append('svg')
   	  visGrp = visSvg.append('g'),
   	  grpYear = visSvg.append('g'),
   	  infoBox = grpYear.append('rect'),
   	  txtYear = grpYear.append('text');

  // D3 Visualization Layer
  function D3Layer() {

    var layer = {},
   	  	bounds,
   	  	feature,
   	  	collection,
   	  	firstDraw = true,
        magExtent, 
        dayExtent,
        eqRadius,
        eqDelay,
        eqDuration,
        eqColor;
        
   	layer.parent = visDiv.node();

   	layer.project = function(coord) {
   	  var svgPoint = layer.map.locationPoint({ lat: coord[1], lon: coord[0] });
   	  return [svgPoint.x, svgPoint.y];
   	};

   	layer.draw = function() {

   	  if (firstDraw) {

   	  	var mapDim = layer.map.dimensions,
		    btnPlay = d3.select('#btnPlay')
   	  		  .on('click', layer.drawPoints);

   	  	visSvg.attr('width',  mapDim.x)
   	  	      .attr('height', mapDim.y);

   	  	var infoPos = {
			    x: mapDim.x - visconf.infoBox.width - visconf.infoBox.margin,
   	  	  y: mapDim.y - visconf.infoBox.height - visconf.infoBox.margin
   	  	};

		    grpYear.attr("transform", "translate(" + infoPos.x + "," + infoPos.y + ")");

		    infoBox.attr('id', 'infobox')
   	  	    .attr('x', 0)
   	  		  .attr('y', 0)
   	  		  .attr('width',  visconf.infoBox.width)
   	  		  .attr('height', visconf.infoBox.height);

   	  	txtYear.attr('id', 'txtyear')
   	  	  .attr('x', visconf.txtInfo.margin.left)
   	  	  .attr('y', visconf.txtInfo.margin.top)
   	  	  .text('1900');

   	  	firstDraw = false;
   	  }

   	};

	layer.drawPoints = function() {

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
        d3.select(this)
          .attr('fill', function() {
            var mag = this.__data__.properties.magnitude;
            return eqColor(Math.floor(mag));
          })
          .attr('fill-opacity', 0.2);
        txtYear.text(this.__data__.properties.year);
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
   	  	.append('path');

      // Compute the data extent
      magExtent = d3.extent(collection.features, function(item) {
          return item.properties.magnitude;
        }),
      dayExtent = d3.extent(collection.features, function(item) {
          return item.properties.day;
        });

      // Compute the delay, color, radius and duration scales
      eqRadius = d3.scale.pow()
        .domain(magExtent)
        .rangeRound(visconf.radExtent)
        .exponent(visconf.radExp),
      eqDelay = d3.scale.linear()
        .domain(dayExtent)
        .rangeRound([10, visconf.duration]),
      eqDuration = d3.scale.linear()
        .domain(magExtent)
        .rangeRound(visconf.durationEntent),
      eqColor = d3.scale.linear()
        .domain(magExtent)
        .range(visconf.colorExtent);

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
   	d3.json('/earthquake/data/full.json', function(earthquakeData) {

   	  // Add additional data to the eartquake events
      var earthquakePoints = earthquakeData.features, 
          firstDate = earthquakePoints[0].properties.datetime,
          dayOffset = Math.abs(epochDay(firstDate));

      earthquakePoints.forEach(function(item) {
      	var datetime = new Date(item.properties.datetime);
      	item.properties['day'] = epochDay(datetime) + dayOffset;
      	item.properties['year'] = datetime.getFullYear();
      });

  	  // Load and draw the map
  	  mapbox.load(mapconf.mapid, function(mbmap) {

        map = mapbox.map("map", mbmap.layer, null, []);
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