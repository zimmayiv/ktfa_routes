    // DRAWING SECTION BEGIN
  
    // Feature group to store drawn items
    const drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    // Initialize Leaflet Draw controls
    const drawControl = new L.Control.Draw({
      edit: {
        featureGroup: drawnItems,
      },
      draw: {
        polyline: true,
        polygon: false,
        circle: false,
        rectangle: false,
        marker: true,
      },
    });
    map.addControl(drawControl);

    // Handle creation of new layers
    map.on(L.Draw.Event.CREATED, function (e) {
      const layer = e.layer;

      // If the drawn layer is a marker
      if (layer instanceof L.Marker) {
        showAnnotationInput(layer);
      }

      // Add the new layer to the feature group
      drawnItems.addLayer(layer);
    });

    // Custom input for annotations
    function showAnnotationInput(layer) {
      const inputContainer = document.createElement('div');
      inputContainer.style.position = 'absolute';
      inputContainer.style.top = '10px';
      inputContainer.style.left = '10px';
      inputContainer.style.zIndex = '1000';
      inputContainer.style.backgroundColor = 'white';
      inputContainer.style.padding = '10px';
      inputContainer.style.border = '1px solid #ccc';
      inputContainer.style.borderRadius = '5px';

      const input = document.createElement('input');
      input.type = 'text';
      input.placeholder = 'Enter a note for this marker';
      input.style.marginRight = '5px';

      const saveButton = document.createElement('button');
      saveButton.textContent = 'Save';
      saveButton.style.marginRight = '5px';

      const cancelButton = document.createElement('button');
      cancelButton.textContent = 'Cancel';

      inputContainer.appendChild(input);
      inputContainer.appendChild(saveButton);
      inputContainer.appendChild(cancelButton);
      document.body.appendChild(inputContainer);

      saveButton.addEventListener('click', () => {
        const note = input.value.trim();
        if (note) {
          layer.bindPopup(note).openPopup();
        }
        document.body.removeChild(inputContainer);
      });

      cancelButton.addEventListener('click', () => {
        document.body.removeChild(inputContainer);
        drawnItems.removeLayer(layer); // Remove the marker if canceled
      });
    }
    // DRAWING SECTION END

    function getLineStringLayers() {
       const layers = drawnItems.getLayers(); // Retrieve all layers in drawnItems

       // Filter only the LineString layers
       const lineStringLayers = layers.filter((layer) => {
          const geoJson = layer.toGeoJSON();
          return geoJson.geometry.type === "LineString";
       });
       return lineStringLayers;
    }

    function generateGoogleMapsUrl(lineStringLayer) {
      // Extract the coordinates from the LineString layer
      const coordinates = lineStringLayer.toGeoJSON().geometry.coordinates;

      // Check if there are at least two coordinates (start and end point)
      if (coordinates.length < 2) {
	console.error("LineString must have at least two coordinates for navigation.");
	return null;
      }

      // Format the coordinates for Google Maps
      const waypoints = coordinates
	.slice(1, -1) // Exclude the start and end points for waypoints
	.map(coord => coord.reverse().join(",")) // Reverse [lng, lat] to [lat, lng]
	.join("|");

      const start = coordinates[0].reverse().join(","); // First coordinate as start
      const end = coordinates[coordinates.length - 1].reverse().join(","); // Last coordinate as end

      // Construct the Google Maps URL
      let googleMapsUrl = `https://www.google.com/maps/dir/?api=1&origin=${start}&destination=${end}`;

      // Add waypoints if they exist
      if (waypoints) {
	googleMapsUrl += `&waypoints=${waypoints}`;
      }

      console.log("Google Maps URL:", googleMapsUrl);
      return googleMapsUrl;
    }

    // Save all layers to GeoJSON
    document.getElementById('save-btn').addEventListener('click', () => {
      const data = drawnItems.toGeoJSON();
      const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);

      const a = document.createElement('a');
      a.href = url;
      const today = new Date();
      const dateString = today.toISOString().slice(0, 10).replace(/-/g, '');
      const route = document.getElementById('route').value;
      const defaultFilename = `${route}-${dateString}.geojson`;
      const userFilename = prompt('Enter filename:', defaultFilename);
      if (userFilename) {
         a.download = userFilename.endsWith('.geojson') ? userFilename : userFilename + '.geojson';
         a.click();
      }

      URL.revokeObjectURL(url);
    });

    document.getElementById('nav-btn').addEventListener('click', () => {
       const lines = getLineStringLayers();
       console.log(lines);
       if (lines.length == 0) { alert("No route drawn."); }
       else {
          const url = generateGoogleMapsUrl(lines[0]);
          window.open(url, "_blank");
       }
    });

    // Load layers from a GeoJSON file
    document.getElementById('load-geojson').addEventListener('change', (event) => {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
          const geojsonData = JSON.parse(e.target.result);

          L.geoJSON(geojsonData, {
            onEachFeature: function (feature, layer) {
              if (feature.properties && feature.properties.popupContent) {
                layer.bindPopup(feature.properties.popupContent);
              }
              drawnItems.addLayer(layer);
            },
          }).addTo(map);
        };
        reader.readAsText(file);
      }
    });
