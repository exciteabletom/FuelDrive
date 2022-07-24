let map = L.map("map").setView([-31.876857, 116.045207], 10);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
}).addTo(map);

window.numbers = {
  "start": 1,
  "end": 1
}
function set_address_number(address, variable) {
  numbers[variable] = address.match(/^\d*/g).join("");
}

function display_address_number(variable) {
  if (window.numbers[variable]) {
    console.log(variable);
    let el = document.getElementById(variable + "Address");
    el.value = window.numbers[variable] + " " + el.value;
  }
}
// minimal configure
const start = new Autocomplete("startAddress", {
  // default selects the first item in
  // the list of results
  selectFirst: true,

  // The number of characters entered should start searching
  howManyCharacters: 2,
  old_marker: null,

  // onSearch
  onSearch: ({ currentValue }) => {
    // You can also use static files
    // const api = '../static/search.json'
    const api = `https://nominatim.openstreetmap.org/search?format=geojson&limit=5&countrycodes=au&q=${encodeURI(
      currentValue + ", Western Australia"
    )}`;
    set_address_number(currentValue, "start")

    return new Promise((resolve) => {
      fetch(api)
        .then((response) => response.json())
        .then((data) => {
          resolve(data.features);
        })
        .catch((error) => {
          console.error(error);
        });
    });
  },
  // nominatim GeoJSON format parse this part turns json into the list of
  // records that appears when you type.
  onResults: ({ currentValue, matches, template }) => {
    const regex = new RegExp(currentValue, "gi");

    // if the result returns 0 we
    // show the no results element
    return matches === 0
      ? template
      : matches
          .map((element) => {
            return `
          <li class="loupe">
            <p>
              ${element.properties.display_name.replace(
                regex,
                (str) => `<b>${str}</b>`
              )}
            </p>
          </li> `;
          })
          .join("");
  },

  // we add an action to enter or click
  onSubmit: ({ object }) => {
    if (this.old_marker) this.old_marker.remove();
    // remove all layers from the map
    map.eachLayer(function (layer) {
      if (!!layer.toGeoJSON) {
        map.removeLayer(layer);
      }
    });

    display_address_number("start");

    const { display_name } = object.properties;
    const [lng, lat] = object.geometry.coordinates;

    const marker = L.marker([lat, lng], {
      title: display_name,
    });

    marker.addTo(map).bindPopup(display_name);
    window.start_coords = `${lat},${lng}`
    this.old_marker = marker;
    map.setView([lat, lng], 10);
  },

  // get index and data from li element after
  // hovering over li with the mouse or using
  // arrow keys ↓ | ↑
  onSelectedItem: ({ index, element, object }) => {
    console.log("onSelectedItem:", index, element, object);
  },

  // the method presents no results element
  noResults: ({ currentValue, template }) =>
    template(`<li>No results found: "${currentValue}"</li>`),
});


const end = new Autocomplete("endAddress", {
  // default selects the first item in
  // the list of results
  selectFirst: true,

  // The number of characters entered should start searching
  howManyCharacters: 2,
  oldMarker: null,

  // onSearch
  onSearch: ({ currentValue }) => {
    // You can also use static files
    // const api = '../static/search.json'
    const api = `https://nominatim.openstreetmap.org/search?format=geojson&limit=5&countrycodes=au&q=${encodeURI(
        currentValue + ", Western Australia"
    )}`;
    set_address_number(currentValue, "end");


    return new Promise((resolve) => {
      fetch(api)
          .then((response) => response.json())
          .then((data) => {
            resolve(data.features);
          })
          .catch((error) => {
            console.error(error);
          });
    });
  },
  // nominatim GeoJSON format parse this part turns json into the list of
  // records that appears when you type.
  onResults: ({ currentValue, matches, template }) => {
    const regex = new RegExp(currentValue, "gi");

    // if the result returns 0 we
    // show the no results element
    return matches === 0
        ? template
        : matches
            .map((element) => {
              return `
          <li class="loupe">
            <p>
              ${element.properties.display_name.replace(
                  regex,
                  (str) => `<b>${str}</b>`
              )}
            </p>
          </li> `;
            })
            .join("");
  },

  // we add an action to enter or click
  onSubmit: ({ object }) => {
    if (this.old_marker) this.old_marker.remove();
    // remove all layers from the map
    map.eachLayer(function (layer) {
      if (!!layer.toGeoJSON) {
        map.removeLayer(layer);
      }
    });
    display_address_number("end");

    const { display_name } = object.properties;
    const [lng, lat] = object.geometry.coordinates;

    const marker = L.marker([lat, lng]);
    marker.addTo(map).bindPopup(display_name);
    window.end_coords = `${lat},${lng}`;
    this.old_marker = marker;
    map.setView([lat, lng], 10);
  },

  // get index and data from li element after
  // hovering over li with the mouse or using
  // arrow keys ↓ | ↑
  onSelectedItem: ({ index, element, object }) => {
    console.log("onSelectedItem:", index, element, object);
  },

  // the method presents no results element
  noResults: ({ currentValue, template }) =>
      template(`<li>No results found: "${currentValue}"</li>`),
});

const form = document.getElementById("main-form");
form.addEventListener("submit", () => {
  document.getElementById("startCoords").value = window.start_coords;
  document.getElementById("endCoords").value = window.end_coords;
})
form.addEventListener("load", () => {
  form.reset();
})
