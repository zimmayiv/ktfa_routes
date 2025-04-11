    function getLineStringLayers() {
       const layers = drawnItems.getLayers(); // Retrieve all layers in drawnItems

       // Filter only the LineString layers
       const lineStringLayers = layers.filter((layer) => {
          const geoJson = layer.toGeoJSON();
          return geoJson.geometry.type === "LineString";
       });
       return lineStringLayers;
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
      const defaultFilename = `newroute-${dateString}.geojson`;
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

