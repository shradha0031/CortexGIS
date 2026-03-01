// app/lib/taskExecutor.ts
// app/lib/taskExecutor.ts

import { geocodePlace } from "./utils";
import { point, buffer, distance } from "@turf/turf";
import type { Task } from "./taskBuilder";

export async function executeTask(
  task: Task,
  setCoords: (coords: { lat: number; lon: number }) => void,
  setZoom: (zoom: number) => void,
  setBuffer: (buffer: any) => void
) {
  switch (task.type) {
    case "GEOCODE":
      if (task.place) {
        const coords = await geocodePlace(task.place);
        setCoords(coords);
      }
      break;

    case "ZOOM":
      if (task.zoomLevel) {
        setZoom(task.zoomLevel);
      }
      break;

    case "BUFFER":
      if (task.coords && task.distance) {
        const pt = point([task.coords.lon, task.coords.lat]);
        const buffered = buffer(pt, task.distance, { units: "kilometers" });
        console.log("Buffer GeoJSON:", buffered);
        setBuffer(buffered);
      }
      break;

    case "MEASURE":
      if (task.coords1 && task.coords2) {
        const pt1 = point([task.coords1.lon, task.coords1.lat]);
        const pt2 = point([task.coords2.lon, task.coords2.lat]);
        const dist = distance(pt1, pt2, { units: "kilometers" });

        // For now, show result as an alert or console log.
        // Later, you can pass this into ChatPanel for feedback messages.
        alert(
          `Distance between ${task.place1} and ${task.place2}: ${dist.toFixed(
            2
          )} km`
        );
      }
      break;

    default:
      console.warn("Unknown task type:", task);
  }
}