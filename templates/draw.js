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

