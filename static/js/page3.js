document.addEventListener("DOMContentLoaded", () => {
  const map = L.map("map", {
    crs: L.CRS.Simple,
    minZoom: -1,
    maxZoom: 2,
  });

  const bounds = [[0, 0], [1000, 1000]];
  L.imageOverlay("/static/images/map.png", bounds).addTo(map);
  map.fitBounds(bounds);

  let selectedCoords = null;
  let selectedDistrict = null;
  let marker = null;

  const searchBox = document.getElementById("search-box");
  const searchButton = document.getElementById("search-button");
  const analyzeButton = document.getElementById("analyze-button");
  const locationText = document.getElementById("selected-location");
  const placeText = document.getElementById("place");
  const panelsText = document.getElementById("panels");

  function updateSelectedLocation(name, lat, lon) {
    selectedDistrict = name;
    selectedCoords = { lat, lon };
    locationText.textContent = `Selected Location: ${name}`;
  }

  function searchLocation() {
    const searchValue = searchBox.value.trim();
    if (!searchValue) {
      alert("Please enter a location to search.");
      return;
    }

    fetch(`/geocode?q=${encodeURIComponent(searchValue)}`)
      .then(res => res.json())
      .then(data => {
        if (data.results && data.results.length > 0) {
          const result = data.results[0];
          updateSelectedLocation(result.formatted, result.geometry.lat, result.geometry.lng);
        } else {
          alert("Location not found.");
        }
      })
      .catch(err => {
        console.error("Search error:", err);
        alert("Error searching location.");
      });
  }

  searchButton.addEventListener("click", searchLocation);

  analyzeButton.addEventListener("click", () => {
    if (!selectedDistrict || !selectedCoords) {
      alert("Please select a location first.");
      return;
    }

    fetch("/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        district: selectedDistrict,
        latitude: selectedCoords.lat,
        longitude: selectedCoords.lon,
      }),
    })
      .then(response => {
        if (response.redirected) {
          window.location.href = response.url;
        } else {
          return response.json().then(data => {
            placeText.textContent = data.error || "No analysis found.";
          });
        }
      })
      .catch(error => {
        console.error("Analyze error:", error);
        placeText.textContent = "Error analyzing location.";
      });
  });
});

// Popup menu functions outside DOMContentLoaded (no DOM dependencies)
function toggleMenu() {
  const menu = document.getElementById('popup-menu');
  menu.style.display = (menu.style.display === "block") ? "none" : "block";
}

function openInstallationPlace() {
  alert("Installation Place clicked");
  window.location.href = "/page5";
}

function openNoOfPanels() {
  alert("No. of Panels clicked");
  window.location.href = "/page6";
}