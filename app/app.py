import reflex as rx
import reflex_enterprise as rxe
from app.components.sidebar import sidebar
from app.state import State
from reflex_enterprise.components.map.types import latlng


def map_view() -> rx.Component:
    """The main map component with markers and buffers."""
    return rxe.map(
        rxe.map.tile_layer(
            url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png",
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        ),
        rx.foreach(
            State.points,
            lambda p: rxe.map.marker(
                rxe.map.tooltip(p["name"]), position=latlng(lat=p["lat"], lng=p["lng"])
            ),
        ),
        rx.foreach(
            State.buffer_geometries,
            lambda g: rx.match(
                g["type"],
                (
                    "circle",
                    rxe.map.circle(
                        center=g["center"],
                        radius=g["radius"],
                        path_options=g["path_options"],
                    ),
                ),
                (
                    "rectangle",
                    rxe.map.rectangle(
                        bounds=g["bounds"], path_options=g["path_options"]
                    ),
                ),
                rx.fragment(),
            ),
        ),
        rxe.map.zoom_control(position="bottomright"),
        id="map-view",
        center=State.map_center,
        zoom=State.map_zoom,
        height="100%",
        width="100%",
        class_name="rounded-2xl shadow-lg border border-gray-200",
        on_click=State.handle_map_click,
        zoom_control=False,
    )


def index() -> rx.Component:
    return rx.el.main(
        rx.el.div(
            sidebar(),
            rx.el.div(map_view(), class_name="flex-1 p-6 h-full"),
            class_name="flex flex-row w-screen h-screen bg-white",
        ),
        class_name="font-['Inter'] antialiased",
    )


app = rxe.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
        rx.el.link(
            rel="stylesheet",
            href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",
            integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=",
            cross_origin="",
        ),
    ],
)
app.add_page(index, route="/")