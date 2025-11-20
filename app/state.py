import reflex as rx
from typing import TypedDict, Any, Optional
import csv
import io
import logging
import json
from reflex_enterprise.components.map.types import (
    LatLng,
    latlng,
    LatLngBounds,
    latlng_bounds,
)


class Point(TypedDict):
    name: str
    lat: float
    lng: float


class State(rx.State):
    """The main application state."""

    points: list[Point] = []
    point_name: str = ""
    latitude: str = ""
    longitude: str = ""
    buffer_type: str = "circle"
    buffer_distance: float = 1000.0
    buffer_unit: str = "meters"
    input_error: str = ""
    map_center: LatLng = latlng(lat=40.7128, lng=-74.006)
    map_zoom: float = 4.0
    map_max_bounds: Optional[LatLngBounds] = None

    @rx.event
    def set_point_name(self, value: str):
        self.point_name = value

    @rx.event
    def set_latitude(self, value: str):
        self.latitude = value

    @rx.event
    def set_longitude(self, value: str):
        self.longitude = value

    @rx.event
    def add_point(self):
        """Adds a point from the manual input form."""
        if not self.point_name or not self.latitude or (not self.longitude):
            self.input_error = "All fields are required."
            return
        try:
            lat = float(self.latitude)
            lng = float(self.longitude)
            if not -90 <= lat <= 90:
                raise ValueError("Latitude must be between -90 and 90.")
            if not -180 <= lng <= 180:
                raise ValueError("Longitude must be between -180 and 180.")
            new_point: Point = {"name": self.point_name, "lat": lat, "lng": lng}
            self.points.append(new_point)
            self.point_name = ""
            self.latitude = ""
            self.longitude = ""
            self.input_error = ""
        except ValueError as e:
            logging.exception(f"Error adding point: {e}")
            self.input_error = f"Invalid coordinates: {e}"
        self._update_map_view()

    @rx.event
    def delete_point(self, point_name: str):
        """Deletes a point from the list."""
        self.points = [p for p in self.points if p["name"] != point_name]
        self._update_map_view()

    @rx.event
    async def handle_csv_upload(self, files: list[rx.UploadFile]):
        """Handles CSV file upload and parses the data."""
        if not files:
            return
        try:
            upload_data = await files[0].read()
            file_content = io.StringIO(upload_data.decode("utf-8"))
            reader = csv.DictReader(file_content)
            new_points = []
            required_headers = ["name", "lat", "lng"]
            if not all((h in reader.fieldnames for h in required_headers)):
                self.input_error = "CSV must have 'name', 'lat', and 'lng' columns."
                return
            for row in reader:
                try:
                    lat = float(row["lat"])
                    lng = float(row["lng"])
                    if not -90 <= lat <= 90 or not -180 <= lng <= 180:
                        continue
                    new_points.append({"name": row["name"], "lat": lat, "lng": lng})
                except (ValueError, KeyError) as e:
                    logging.exception(f"Skipping invalid row in CSV: {row} - {e}")
                    continue
            self.points.extend(new_points)
            self.input_error = ""
            self._update_map_view()
        except Exception as e:
            logging.exception(f"Failed to process CSV: {e}")
            self.input_error = f"Failed to process CSV: {e}"

    @rx.event
    def set_buffer_type(self, type: str):
        self.buffer_type = type

    @rx.event
    def set_buffer_distance(self, distance: str):
        try:
            self.buffer_distance = float(distance)
        except ValueError as e:
            logging.exception(f"Invalid buffer distance value: {distance} - {e}")
            pass

    @rx.event
    def clear_all_points(self):
        self.points = []
        self.input_error = ""
        self.map_max_bounds = None
        self.map_center = latlng(lat=40.7128, lng=-74.006)
        self.map_zoom = 4.0

    @rx.event
    def handle_map_click(self, event: dict):
        """Adds a point when the map is clicked."""
        lat = round(event["latlng"]["lat"], 6)
        lng = round(event["latlng"]["lng"], 6)
        new_point_name = f"Point {len(self.points) + 1}"
        new_point: Point = {"name": new_point_name, "lat": lat, "lng": lng}
        self.points.append(new_point)
        self._update_map_view()

    def _update_map_view(self):
        """Helper to update map bounds and center based on points."""
        if not self.points:
            self.map_max_bounds = None
            self.map_center = latlng(lat=40.7128, lng=-74.006)
            self.map_zoom = 4.0
            return
        lats = [p["lat"] for p in self.points]
        lngs = [p["lng"] for p in self.points]
        corner1_lat = min(lats)
        corner1_lng = min(lngs)
        corner2_lat = max(lats)
        corner2_lng = max(lngs)
        if len(self.points) == 1:
            self.map_center = latlng(lat=lats[0], lng=lngs[0])
            self.map_zoom = 13.0
            self.map_max_bounds = None
        else:
            self.map_max_bounds = latlng_bounds(
                corner1_lat=corner1_lat,
                corner1_lng=corner1_lng,
                corner2_lat=corner2_lat,
                corner2_lng=corner2_lng,
            )

    @rx.var
    def buffer_geometries(self) -> list[dict]:
        """Computes buffer geometries for the map."""
        if not self.points:
            return []
        geometries = []
        for point in self.points:
            if self.buffer_type == "circle":
                geometries.append(
                    {
                        "type": "circle",
                        "center": latlng(lat=point["lat"], lng=point["lng"]),
                        "radius": self.buffer_distance,
                        "path_options": {
                            "color": "#8B5CF6",
                            "fillColor": "#A78BFA",
                            "fillOpacity": 0.3,
                        },
                    }
                )
            elif self.buffer_type == "square":
                import math

                lat_deg_per_meter = 1 / 111132.954
                lng_deg_per_meter = 1 / (111320 * math.cos(math.radians(point["lat"])))
                lat_offset = self.buffer_distance / 2 * lat_deg_per_meter
                lng_offset = self.buffer_distance / 2 * lng_deg_per_meter
                bounds = latlng_bounds(
                    corner1_lat=point["lat"] - lat_offset,
                    corner1_lng=point["lng"] - lng_offset,
                    corner2_lat=point["lat"] + lat_offset,
                    corner2_lng=point["lng"] + lng_offset,
                )
                geometries.append(
                    {
                        "type": "rectangle",
                        "bounds": bounds,
                        "path_options": {
                            "color": "#8B5CF6",
                            "fillColor": "#A78BFA",
                            "fillOpacity": 0.3,
                        },
                    }
                )
        return geometries

    @rx.var
    def result_summary(self) -> dict[str, str | int]:
        """Provides a summary of the current data."""
        num_points = len(self.points)
        num_buffers = len(self.buffer_geometries)
        return {
            "points": num_points,
            "buffers": num_buffers,
            "distance": f"{self.buffer_distance:.2f} meters",
            "shape": self.buffer_type.capitalize(),
        }

    def _get_geojson_data(self) -> dict:
        """Helper to generate GeoJSON feature collection."""
        features = []
        for point in self.points:
            features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [point["lng"], point["lat"]],
                    },
                    "properties": {"name": point["name"]},
                }
            )
        for geometry in self.buffer_geometries:
            if geometry["type"] == "circle":
                import math

                center_lat = geometry["center"]["lat"]
                center_lng = geometry["center"]["lng"]
                radius_m = geometry["radius"]
                lat_deg_per_meter = 1 / 111132.954
                lng_deg_per_meter = 1 / (111320 * math.cos(math.radians(center_lat)))
                lat_radius = radius_m * lat_deg_per_meter
                lng_radius = radius_m * lng_deg_per_meter
                circle_points = []
                for i in range(32):
                    angle = i / 32 * 2 * math.pi
                    dx = lng_radius * math.cos(angle)
                    dy = lat_radius * math.sin(angle)
                    circle_points.append([center_lng + dx, center_lat + dy])
                circle_points.append(circle_points[0])
                features.append(
                    {
                        "type": "Feature",
                        "geometry": {"type": "Polygon", "coordinates": [circle_points]},
                        "properties": {"type": "buffer", "shape": "circle"},
                    }
                )
            elif geometry["type"] == "rectangle":
                bounds = geometry["bounds"]
                coords = [
                    [
                        [bounds[0][1], bounds[0][0]],
                        [bounds[1][1], bounds[0][0]],
                        [bounds[1][1], bounds[1][0]],
                        [bounds[0][1], bounds[1][0]],
                        [bounds[0][1], bounds[0][0]],
                    ]
                ]
                features.append(
                    {
                        "type": "Feature",
                        "geometry": {"type": "Polygon", "coordinates": coords},
                        "properties": {"type": "buffer", "shape": "square"},
                    }
                )
        return {"type": "FeatureCollection", "features": features}

    @rx.event
    def download_geojson(self):
        """Generates and downloads the data as a GeoJSON file."""
        if not self.points:
            return rx.toast("No data to export.")
        geojson_data = self._get_geojson_data()
        return rx.download(
            data=json.dumps(geojson_data, indent=2).encode("utf-8"),
            filename="geobuffer_export.geojson",
        )

    @rx.event
    def download_shapefile(self):
        """Generates and downloads the data as a Shapefile (.zip)."""
        if not self.points:
            return rx.toast("No data to export.")
        try:
            import shapefile
            from zipfile import ZipFile

            geojson_data = self._get_geojson_data()
            zip_buffer = io.BytesIO()
            point_features = [
                f for f in geojson_data["features"] if f["geometry"]["type"] == "Point"
            ]
            buffer_features = [
                f
                for f in geojson_data["features"]
                if f["geometry"]["type"] == "Polygon"
            ]
            with ZipFile(zip_buffer, "w") as zip_f:
                if point_features:
                    shp_buffer = io.BytesIO()
                    shx_buffer = io.BytesIO()
                    dbf_buffer = io.BytesIO()
                    with shapefile.Writer(
                        shp=shp_buffer, shx=shx_buffer, dbf=dbf_buffer
                    ) as w:
                        w.field("name", "C")
                        for feature in point_features:
                            w.point(*feature["geometry"]["coordinates"])
                            w.record(name=feature["properties"].get("name", ""))
                    zip_f.writestr("points.shp", shp_buffer.getvalue())
                    zip_f.writestr("points.shx", shx_buffer.getvalue())
                    zip_f.writestr("points.dbf", dbf_buffer.getvalue())
                if buffer_features:
                    shp_buffer = io.BytesIO()
                    shx_buffer = io.BytesIO()
                    dbf_buffer = io.BytesIO()
                    with shapefile.Writer(
                        shp=shp_buffer, shx=shx_buffer, dbf=dbf_buffer
                    ) as w:
                        w.field("type", "C")
                        w.field("shape", "C")
                        for feature in buffer_features:
                            w.poly(feature["geometry"]["coordinates"])
                            w.record(
                                type=feature["properties"].get("type", ""),
                                shape=feature["properties"].get("shape", ""),
                            )
                    zip_f.writestr("buffers.shp", shp_buffer.getvalue())
                    zip_f.writestr("buffers.shx", shx_buffer.getvalue())
                    zip_f.writestr("buffers.dbf", dbf_buffer.getvalue())
                prj_wkt = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]'
                if point_features:
                    zip_f.writestr("points.prj", prj_wkt)
                if buffer_features:
                    zip_f.writestr("buffers.prj", prj_wkt)
            return rx.download(
                data=zip_buffer.getvalue(), filename="geobuffer_export.zip"
            )
        except Exception as e:
            logging.exception(f"Failed to generate Shapefile: {e}")
            return rx.toast("Failed to generate Shapefile.")