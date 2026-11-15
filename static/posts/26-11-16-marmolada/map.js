(async () => {
  const status = document.querySelector('#status');
  const fallback = document.querySelector('#fallback');
  const slider = document.querySelector('#distance');
  const readout = document.querySelector('#readout');
  const view3d = document.querySelector('#view3d');
  const view2d = document.querySelector('#view2d');
  const reset = document.querySelector('#reset');
  let map;
  try {
    const [response, mediaResponse] = await Promise.all([fetch('route.json'), fetch('media.json')]);
    if (!response.ok || !mediaResponse.ok) throw new Error('Route data unavailable');
    const route = await response.json();
    const media = await mediaResponse.json();
    const coordinates = route.coordinates;
    const summary = route.summary;
    const highest = coordinates[summary.highestIndex];
    const feature = coords => ({type: 'Feature', properties: {}, geometry: {type: 'Point', coordinates: coords.slice(0, 2)}});
    const duration = window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 650;
    slider.max = coordinates.length - 1;
    const updateReadout = index => {
      const point = coordinates[index];
      const label = `${route.distanceKm[index].toFixed(1)} km · ${Math.round(point[2]).toLocaleString()} m`;
      readout.textContent = label;
      slider.setAttribute('aria-valuetext', label);
      if (map && map.getSource('position')) map.getSource('position').setData(feature(point));
    };
    slider.addEventListener('input', () => updateReadout(Number(slider.value)));
    updateReadout(0);
    if (!window.maplibregl) throw new Error('Map library unavailable');
    map = new maplibregl.Map({
      container: 'map',
      center: [(summary.bounds[0][0] + summary.bounds[1][0]) / 2, (summary.bounds[0][1] + summary.bounds[1][1]) / 2],
      zoom: 11.5, pitch: 60, bearing: -25, maxZoom: 16, maxPitch: 75,
      cooperativeGestures: true,
      style: {
        version: 8,
        sources: {
          basemap: {type: 'raster', tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'], tileSize: 256, maxzoom: 19, attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'},
          terrain: {type: 'raster-dem', url: 'https://tiles.mapterhorn.com/tilejson.json', encoding: 'terrarium', tileSize: 512, maxzoom: 12},
          hillshade: {type: 'raster-dem', url: 'https://tiles.mapterhorn.com/tilejson.json', encoding: 'terrarium', tileSize: 512, maxzoom: 12}
        },
        layers: [
          {id: 'basemap', type: 'raster', source: 'basemap'},
          {id: 'hillshade', type: 'hillshade', source: 'hillshade', paint: {'hillshade-shadow-color': '#535c45', 'hillshade-exaggeration': 0.35}}
        ],
        terrain: {source: 'terrain', exaggeration: 1}
      }
    });
    // Bound tile requests to the area actually explored; no prefetch or downloads.
    map.addControl(new maplibregl.NavigationControl({visualizePitch: true}), 'top-right');
    map.addControl(new maplibregl.FullscreenControl(), 'top-right');
    map.addControl(new maplibregl.ScaleControl({maxWidth: 100, unit: 'metric'}), 'bottom-left');
    function fit() {
      map.fitBounds(summary.bounds, {padding: {top: 65, bottom: 45, left: 40, right: 55}, maxZoom: 12.5,
        pitch: view3d.getAttribute('aria-pressed') === 'true' ? 60 : 0,
        bearing: view3d.getAttribute('aria-pressed') === 'true' ? -25 : 0, duration});
    }
    function view(threeD) {
      view3d.setAttribute('aria-pressed', String(threeD));
      view2d.setAttribute('aria-pressed', String(!threeD));
      map.setTerrain(threeD ? {source: 'terrain', exaggeration: 1} : null);
      fit();
    }
    view3d.addEventListener('click', () => view(true));
    view2d.addEventListener('click', () => view(false));
    reset.addEventListener('click', fit);
    map.on('error', event => {
      // Keep the locally hosted outline visible when the map cannot initialise.
      if (!map.isStyleLoaded() && !fallback.hidden) {
        status.textContent = 'The interactive tiles could not load. The recorded route outline and elevation profile are still available.';
      } else if (event.error && /terrain|mapterhorn/i.test(event.error.message)) {
        status.textContent = 'Some terrain tiles could not load. Try the overhead view, or use the route outline and elevation profile.';
      }
    });
    map.on('load', () => {
      map.addSource('route', {type: 'geojson', data: {type: 'Feature', properties: {}, geometry: {type: 'LineString', coordinates: coordinates.map(p => p.slice(0, 2))}}});
      map.addLayer({id: 'route-casing', type: 'line', source: 'route', layout: {'line-cap': 'round', 'line-join': 'round'}, paint: {'line-color': '#fffefa', 'line-width': 7}});
      map.addLayer({id: 'route-line', type: 'line', source: 'route', layout: {'line-cap': 'round', 'line-join': 'round'}, paint: {'line-color': '#2f5948', 'line-width': 4}});
      map.addSource('position', {type: 'geojson', data: feature(coordinates[0])});
      map.addLayer({id: 'position-dot', type: 'circle', source: 'position', paint: {'circle-radius': 6, 'circle-color': '#946a2f', 'circle-stroke-color': 'white', 'circle-stroke-width': 2}});
      new maplibregl.Marker({color: '#946a2f', scale: 0.7}).setLngLat(highest).setPopup(new maplibregl.Popup().setText('Punta Penia · highest recorded elevation 3,349 m')).addTo(map);
      for (const item of media.filter(item => item.mapLabel)) {
        const button = document.createElement('button');
        button.className = 'media-marker';
        button.dataset.mediaId = item.id;
        button.textContent = item.mapLabel;
        button.setAttribute('aria-label', `${item.time} · ${item.caption}`);
        const card = document.createElement('div');
        card.className = 'media-popup';
        const image = document.createElement('img');
        image.src = item.thumbnail;
        image.alt = item.caption;
        image.width = 180;
        image.loading = 'lazy';
        const label = document.createElement('p');
        label.textContent = `${item.time} · ${item.caption}`;
        const position = document.createElement('p');
        position.textContent = `${item.distanceKm.toFixed(1)} km · ${item.elevationM.toLocaleString()} m${item.positionMethod === 'capture time' ? ' · approximate position, matched by time' : ''}`;
        const link = document.createElement('a');
        link.href = new URL(`./#media-${item.id}`, window.location.href).href;
        link.target = '_parent';
        link.textContent = item.type === 'video' ? 'Watch in the post →' : 'See in the post →';
        card.append(image, label, position, link);
        new maplibregl.Marker({element: button}).setLngLat(item.coordinate)
          .setPopup(new maplibregl.Popup({offset: 16, maxWidth: '220px'}).setDOMContent(card)).addTo(map);
      }
      fallback.hidden = true;
      for (const control of [view3d, view2d, reset, slider]) control.disabled = false;
      status.textContent = 'Numbered markers open photos and videos. Drag to pan; right-drag or use two fingers to tilt. The slider follows the recorded route. Terrain is shown at its natural height.';
      fit();
      map.once('idle', () => { document.body.dataset.mapReady = 'true'; });
    });
  } catch (error) {
    if (map) map.remove();
    fallback.hidden = false;
    status.textContent = 'Interactive 3D is unavailable in this browser. The recorded route outline and elevation profile are shown instead.';
  }
})();
