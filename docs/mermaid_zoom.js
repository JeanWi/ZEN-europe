// Scroll to zoom and drag to pan the diagrams that have the :zoom: option.
// sphinxcontrib-mermaid does not add zoom to them when its fullscreen button is on,
// and its global d3 is not defined because the require.js of nbsphinx captures it.
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7.9.0/+esm";

const attachZoom = () => {
  document
    .querySelectorAll(".mermaid[data-zoom-id] > svg:not([data-zoom])")
    .forEach((element) => {
      element.setAttribute("data-zoom", "");
      const svg = d3.select(element);
      svg.html("<g>" + svg.html() + "</g>");
      const inner = svg.select("g");
      svg.call(
        d3.zoom().on("zoom", (event) => inner.attr("transform", event.transform))
      );
    });
};

// diagrams are rendered, and rendered again on theme changes, by sphinxcontrib-mermaid
attachZoom();
new MutationObserver(attachZoom).observe(document.body, {
  childList: true,
  subtree: true,
});
