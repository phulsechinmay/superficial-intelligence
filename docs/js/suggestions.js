var intToHex = function(rgb) {
    // convert a decimal number 0-255 to its hex representation
    var hex = Number(rgb).toString(16);
    if (hex.length < 2) {
        hex = '0' + hex;
    }
    return hex;
};

function rgbToHex(r, g, b) {
    // convert r,g,b numbers, each 0-255, to thier hex representation
    return '#' + intToHex(r) + intToHex(g) + intToHex(b);
}

function scale01(x) {
    // transform a list of numbers to be in the range of 0 to 1
    let f = (z) => (z - Math.min(...x)) / (Math.max(...x) - Math.min(...x));
    return x.map(f);
}

const getData = (resource) =>
    // get the json file for comments for each location
    // return a list of objects representating each location
    fetch("/data/" + resource)
        .then((response) => response.json())
        .then((result) =>
            result.map(({ lat, lng, weight, ...other }) => ({
                location: new google.maps.LatLng(lat, lng),
                weight,
                ...other,
            }))
        );

const plotMap = () => {
    // plot locations on a google map
    let map = new google.maps.Map(document.getElementById('map'), {
        center: new google.maps.LatLng(34.037228, -118.416912),
        zoom: 12,
    });

    var transitLayer = new google.maps.TransitLayer();
    transitLayer.setMap(map);

    getData('latlng.json').then((locations) => plotHeatmap(locations, map));
    getData('latlng.json').then((locations) => plotCommentData(locations, map));
    getData('success.json').then((locations) => plotSuccessData(locations, map));
    addLegend(map);
};

const plotHeatmap = (locations, map) => {
    var heatmap = new google.maps.visualization.HeatmapLayer({
        data: locations,
        radius: 20,
    });
    heatmap.setMap(map);
};

const plotSuccessData = (locations, map) => {
    const TOP_N = 10;
    locations = locations.sort((a, b) => (a.weight > b.weight ? -1 : 1));
    let scaledWeights = scale01(locations.map((x) => x.weight));
    for (var i in locations.slice(0, TOP_N)) {
        var marker = new google.maps.Marker({
            position: locations[i].location,
            map: map,
            label: (parseInt(i) + 1).toString(),
        });
    }
};

const plotCommentData = (locations, map) => {
    const TOP_N = 10;
    locations = locations.sort((a, b) => (a.weight > b.weight ? -1 : 1));
    let scaledWeights = scale01(locations.map((x) => x.weight));
    for (var i in locations.slice(0, TOP_N)) {
        let circle = new google.maps.Circle({
            strokeColor: 'red', //rgbToHex(70, 240, Math.floor(scaledWeights[i] * 255)),
            strokeOpacity: 0.5,
            strokeWeight: 2,
            fillColor: 'red', //rgbToHex(70, 240, Math.floor(scaledWeights[i] * 255)),
            fillOpacity: 0.3,
            map: map,
            center: locations[i].location,
            radius: Math.sqrt(500000 * scaledWeights[i]),
            title: locations[i].comment || 'No comments',
            clickable: true,
        });
        let comments = locations[i].comments.filter((x) => x != 'I Agree' && x != '');
        if (comments.length !== 0) {
            let content =
                '<div id="content">' +
                '<h3>' +
                locations[i].weight.toString() +
                ' comments:</h3>' +
                '<ul>' +
                comments.map((c) => '<li>' + c + '</li>') +
                '</ul>' +
                '</div>';
            let infowindow = new google.maps.InfoWindow({
                content: content,
                position: locations[i].location,
            });
            google.maps.event.addListener(circle, 'mouseover', function(ev) {
                infowindow.setPosition(circle.getCenter());
                infowindow.open(map);
            });
            google.maps.event.addListener(circle, 'mouseout', function(ev) {
                infowindow.setPosition(circle.getCenter());
                infowindow.open(null);
            });
        }
    }
};

const addLegend = (map) => {
    var iconBase = 'http://maps.google.com/mapfiles/kml/';
    var icons = {
        success: {
            name: 'Predicted Success',
            icon: iconBase + 'paddle/1.png',
        },
        comments: {
            name: 'Most Comments',
            icon: 'img/red_circle.png',
        },
        // info: {
        //     name: 'Info',
        // },
    };
    var legend = document.getElementById('legend');
    for (var key in icons) {
        var type = icons[key];
        var name = type.name;
        var icon = type.icon;
        var div = document.createElement('div');
        div.setAttribute('style', 'padding: 10px');
        div.innerHTML = '<img src="' + icon + '" height="30" width="30">       ' + name;
        legend.appendChild(div);
    }
    var div = document.createElement('div');
    div.setAttribute('style', 'padding: 10px');
    div.innerHTML = '<b>Heatmap</b> = comment density';
    legend.appendChild(div);

    map.controls[google.maps.ControlPosition.LEFT_BOTTOM].push(legend);
};

function initMap() {
    plotMap();
}
