import reflex as rx
from app.state import State


def _form_input(
    label: str,
    placeholder: str,
    value: rx.Var,
    on_change: rx.event.EventHandler,
    type: str = "text",
) -> rx.Component:
    """A styled input component for forms."""
    return rx.el.div(
        rx.el.label(label, class_name="block text-sm font-medium text-gray-700 mb-1"),
        rx.el.input(
            placeholder=placeholder,
            on_change=on_change,
            type=type,
            class_name="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all",
            default_value=value,
        ),
        class_name="w-full",
    )


def manual_input_panel() -> rx.Component:
    """Panel for manually adding geospatial points."""
    return rx.el.div(
        rx.el.h3("Manual Input", class_name="text-lg font-semibold text-gray-800 mb-4"),
        rx.el.div(
            _form_input(
                "Point Name",
                "e.g., Central Park",
                State.point_name,
                State.set_point_name,
            ),
            _form_input(
                "Latitude",
                "e.g., 40.785091",
                State.latitude,
                State.set_latitude,
                type="number",
            ),
            _form_input(
                "Longitude",
                "e.g., -73.968285",
                State.longitude,
                State.set_longitude,
                type="number",
            ),
            rx.el.button(
                "Add Point",
                rx.icon("circle_plus", class_name="mr-2 h-4 w-4"),
                on_click=State.add_point,
                class_name="w-full mt-4 flex items-center justify-center px-4 py-2 bg-purple-600 text-white font-semibold rounded-lg shadow-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-opacity-75 transition-all duration-150 ease-in-out",
            ),
            rx.cond(
                State.input_error != "",
                rx.el.div(
                    rx.icon("flag_triangle_right", class_name="h-4 w-4 mr-2"),
                    State.input_error,
                    class_name="mt-3 flex items-center text-sm text-red-600 bg-red-50 p-2 rounded-md",
                ),
                None,
            ),
            class_name="flex flex-col gap-3",
        ),
    )


def csv_upload_panel() -> rx.Component:
    """Panel for uploading points via CSV."""
    return rx.el.div(
        rx.el.h3("CSV Upload", class_name="text-lg font-semibold text-gray-800 mb-4"),
        rx.upload.root(
            rx.el.div(
                rx.icon("cloud_upload", class_name="h-8 w-8 text-gray-500"),
                rx.el.p(
                    "Drag & drop a .csv file or click to select",
                    class_name="text-sm text-gray-600 text-center",
                ),
                rx.el.p(
                    "Requires 'name', 'lat', 'lng' columns.",
                    class_name="text-xs text-gray-500 mt-1",
                ),
                class_name="flex flex-col items-center justify-center p-6 gap-2",
            ),
            id="csv-upload",
            border="2px dashed #E4E4E7",
            padding="1rem",
            border_radius="12px",
            bg="#FAFAFA",
            width="100%",
            on_drop=State.handle_csv_upload,
            class_name="cursor-pointer hover:border-purple-400 transition-colors",
        ),
    )


def point_list_panel() -> rx.Component:
    """Panel displaying the list of added points."""
    return rx.el.div(
        rx.el.div(
            rx.el.h3("Data Points", class_name="text-lg font-semibold text-gray-800"),
            rx.el.span(
                f"{State.points.length()} points",
                class_name="text-sm font-medium text-gray-500 bg-gray-100 py-1 px-2.5 rounded-full",
            ),
            class_name="flex justify-between items-center mb-4",
        ),
        rx.el.div(
            rx.cond(
                State.points.length() > 0,
                rx.el.div(
                    rx.foreach(
                        State.points,
                        lambda p: rx.el.div(
                            rx.el.div(
                                rx.el.p(
                                    p["name"],
                                    class_name="font-semibold text-gray-800 truncate",
                                ),
                                rx.el.p(
                                    f"Lat: {p['lat']}, Lng: {p['lng']}",
                                    class_name="text-xs text-gray-500",
                                ),
                                class_name="flex-1 min-w-0",
                            ),
                            rx.el.button(
                                rx.icon("trash-2", class_name="h-4 w-4"),
                                on_click=lambda: State.delete_point(p["name"]),
                                class_name="p-1.5 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors",
                            ),
                            class_name="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-200",
                        ),
                    ),
                    class_name="flex flex-col gap-2 max-h-64 overflow-y-auto",
                ),
                rx.el.div(
                    "No points added yet.",
                    class_name="text-center text-sm text-gray-500 py-8 px-4 bg-gray-50 rounded-lg",
                ),
            )
        ),
        rx.cond(
            State.points.length() > 0,
            rx.el.button(
                "Clear All",
                on_click=State.clear_all_points,
                class_name="w-full mt-4 text-sm text-red-600 hover:bg-red-50 py-2 rounded-lg transition-colors",
            ),
            None,
        ),
    )


def buffer_config_panel() -> rx.Component:
    """Panel for configuring buffer properties."""
    return rx.el.div(
        rx.el.h3(
            "Buffer Configuration",
            class_name="text-lg font-semibold text-gray-800 mb-4",
        ),
        rx.el.div(
            rx.el.label(
                "Buffer Shape",
                class_name="block text-sm font-medium text-gray-700 mb-2",
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("circle", class_name="mr-2 h-4 w-4"),
                    "Circle",
                    on_click=lambda: State.set_buffer_type("circle"),
                    class_name=rx.cond(
                        State.buffer_type == "circle",
                        "flex-1 flex items-center justify-center py-2 px-3 bg-purple-600 text-white rounded-l-lg shadow-sm z-10",
                        "flex-1 flex items-center justify-center py-2 px-3 bg-white text-gray-700 border border-gray-300 rounded-l-lg hover:bg-gray-50",
                    ),
                ),
                rx.el.button(
                    rx.icon("square", class_name="mr-2 h-4 w-4"),
                    "Square",
                    on_click=lambda: State.set_buffer_type("square"),
                    class_name=rx.cond(
                        State.buffer_type == "square",
                        "flex-1 flex items-center justify-center py-2 px-3 bg-purple-600 text-white rounded-r-lg shadow-sm z-10 border-t border-b border-purple-600",
                        "flex-1 flex items-center justify-center py-2 px-3 bg-white text-gray-700 border border-l-0 border-gray-300 rounded-r-lg hover:bg-gray-50",
                    ),
                ),
                class_name="flex w-full",
            ),
            class_name="mb-4",
        ),
        rx.el.div(
            rx.el.label(
                "Distance", class_name="block text-sm font-medium text-gray-700 mb-1"
            ),
            rx.el.input(
                default_value=State.buffer_distance.to_string(),
                on_change=State.set_buffer_distance,
                type="number",
                class_name="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all",
            ),
            class_name="mb-4",
        ),
        rx.el.button(
            "Generate Buffers",
            on_click=rx.toast("Buffers updated on map!"),
            class_name="w-full mt-2 flex items-center justify-center px-4 py-2 bg-green-600 text-white font-semibold rounded-lg shadow-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-opacity-75 transition-all duration-150 ease-in-out",
        ),
    )


def results_panel() -> rx.Component:
    """Panel to display summary and export options."""
    summary_item_class = "flex justify-between items-center text-sm"
    summary_label_class = "text-gray-600"
    summary_value_class = (
        "font-semibold text-gray-800 bg-gray-100 py-0.5 px-2 rounded-md"
    )
    return rx.el.div(
        rx.el.h3(
            "Results & Export", class_name="text-lg font-semibold text-gray-800 mb-4"
        ),
        rx.el.div(
            rx.el.div(
                rx.el.p("Points", class_name=summary_label_class),
                rx.el.p(State.result_summary["points"], class_name=summary_value_class),
                class_name=summary_item_class,
            ),
            rx.el.div(
                rx.el.p("Buffers", class_name=summary_label_class),
                rx.el.p(
                    State.result_summary["buffers"], class_name=summary_value_class
                ),
                class_name=summary_item_class,
            ),
            rx.el.div(
                rx.el.p("Shape", class_name=summary_label_class),
                rx.el.p(State.result_summary["shape"], class_name=summary_value_class),
                class_name=summary_item_class,
            ),
            rx.el.div(
                rx.el.p("Distance", class_name=summary_label_class),
                rx.el.p(
                    State.result_summary["distance"], class_name=summary_value_class
                ),
                class_name=summary_item_class,
            ),
            class_name="space-y-2 p-3 bg-white rounded-lg border border-gray-200",
        ),
        rx.el.div(
            rx.el.button(
                "Export GeoJSON",
                rx.icon("download", class_name="mr-2 h-4 w-4"),
                on_click=State.download_geojson,
                class_name="flex-1 flex items-center justify-center px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-75 transition-all duration-150 ease-in-out",
            ),
            rx.el.button(
                "Export Shapefile (.zip)",
                rx.icon("download", class_name="mr-2 h-4 w-4"),
                on_click=State.download_shapefile,
                class_name="flex-1 flex items-center justify-center px-4 py-2 bg-teal-600 text-white font-semibold rounded-lg shadow-md hover:bg-teal-700 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:ring-opacity-75 transition-all duration-150 ease-in-out",
            ),
            class_name="flex gap-3 mt-4",
        ),
    )


def sidebar() -> rx.Component:
    """The main sidebar component containing all control panels."""
    return rx.el.aside(
        rx.el.div(
            rx.icon("git-commit-horizontal", class_name="h-8 w-8 text-purple-600"),
            rx.el.h1(
                "GeoBuffer",
                class_name="text-2xl font-bold text-gray-900 tracking-tight",
            ),
            class_name="flex items-center gap-3 p-4 border-b border-gray-200",
        ),
        rx.el.div(
            manual_input_panel(),
            rx.el.hr(class_name="my-6 border-gray-200"),
            csv_upload_panel(),
            rx.el.hr(class_name="my-6 border-gray-200"),
            point_list_panel(),
            rx.el.hr(class_name="my-6 border-gray-200"),
            buffer_config_panel(),
            rx.el.hr(class_name="my-6 border-gray-200"),
            results_panel(),
            class_name="p-6 flex-1 overflow-y-auto",
        ),
        class_name="flex flex-col w-[26rem] h-screen bg-gray-50 border-r border-gray-200 shadow-md",
    )