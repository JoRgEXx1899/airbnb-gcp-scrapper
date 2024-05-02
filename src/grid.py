import math

from point import Point

# angle = 50.9465057012392


def create_polygon(point1, point2) -> list[Point]:
    """Function to create a polygon from two points, creating two points of the 
    combination of latitude and longitude of the arg points. Returns a list of 
    four points whichs makes a quadrilateral shape.

    Args:
        point1 (Point): Point with latitude and longitude
        point2 (Point): Point with latitude and longitude

    Returns:
        list[Point]: A list of four points which makes a quadrilateral shape.
    """
    point_lu = Point(point1.lat, point2.lon)
    point_rd = Point(point2.lat, point1.lon)
    # print("Left up point", point_lu.lat, point_lu.lon)
    # print("Right down point", point_rd.lat, point_rd.lon)
    polygon = {"left_up": point_lu,
               "right_up": point1,
               "left_down": point2,
               "right_down": point_rd}
    return polygon


def diagonal_point_45(meters: float, reference_latitude: float, reference_longitude: float) -> Point:
    """Returns the diagonal point at 45 degrees (up right) of the given point 
    at the given horizontal or vertical meters. Calculates the diagonal based on
    the earth ratio '6378137' meters and making conversion and to degrees, minutes 
    and seconds. Makes a reverse conversion from degrees, minutes and seconds to 
    latitude and longitude in degrees.

    Args:
        meters (float): Horizontal or vertical meters to  move the latitude and longitude
        reference_latitude (_type_): the latitude of the reference
        reference_longitude (_type_): the longitude of the reference

    Returns:
        Point: A point traslated in diagonal with the given meters.
    """
    # Earth ratio in meters
    earth_ratio = 6378137.0

    # Conversion from meters to degrees in latitude (1 meter equals to 1/111319.9 degrees)
    delta_lat = meters / earth_ratio * (180 / math.pi)

    # Conversion from meters to degrees in longitude (1 meter is equivalent to 1/(111319.9 * cos(latitude)) degrees)
    delta_long = meters / \
        (earth_ratio * math.cos(math.radians(reference_latitude))) * (180 / math.pi)

    # Conversion to minutes and seconds
    lat_degrees = int(delta_lat)
    lat_minutes = int((delta_lat - lat_degrees) * 60)
    lat_seconds = ((delta_lat - lat_degrees) * 60 - lat_minutes) * 60

    long_degrees = int(delta_long)
    long_minutes = int((delta_long - long_degrees) * 60)
    long_seconds = ((delta_long - long_degrees) * 60 - long_minutes) * 60

    # Add to reference
    new_lat = reference_latitude + lat_degrees + \
        lat_minutes / 60 + lat_seconds / 3600
    new_long = reference_longitude + long_degrees + \
        long_minutes / 60 + long_seconds / 3600

    return Point(new_lat, new_long)


def get_distance_meters(point1: Point, point2: Point) -> float:
    """Function to calculate the distance between two geographic points using Harversine Formula

    Args:
        point1 (Point): Point 1 to calculate the distance
        point2 (Point): Point 2 to calculate the distance

    Returns:
        distance (float): Distance in meters between the tow given points
    """
    # Earth ratio in meters
    earth_ratio = 6378137.0

    # Convert coordinates from degrees to radians
    lat1 = math.radians(point1.lat)
    lon1 = math.radians(point1.lon)
    lat2 = math.radians(point2.lat)
    lon2 = math.radians(point2.lon)

    # Difference of longitude and latitude
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    # Haversine Formula
    a_2 = math.sin(dlat / 2)**2 + math.cos(lat1) * \
        math.cos(lat2) * math.sin(dlon / 2)**2

    c_2 = 2 * math.atan2(math.sqrt(a_2), math.sqrt(1 - a_2))

    # Distance between points
    distance = earth_ratio * c_2

    return distance


def create_grid(polygon, distance) -> list[list[Point]]:
    """Function to create a grid from a polygon with a given distance between 
    points horizontally and vertically. Returns a list of polygons of the given size.

    Args:
        polygon (list[Point]): A list of points which grouped makes a quadrilateral shape 
        distance (_type_): A distance in meters of the grid horizontally and vertically

    Returns:
        list[list[Point]]: A list of polygons of the given size
    """
    # Defines the initial and final points
    start_point = polygon["left_down"]
    final_point = polygon["right_up"]
    # Starts a empty list
    grid = []
    # Verifies if the start point is at left down from the final point
    if (start_point.lat < final_point.lat and start_point.lon < final_point.lon):
        # Defines the first iteration parameters: left_down_point, lat_sum, lon_sum
        left_down_point = start_point
        lat_sum = left_down_point.lat
        lon_sum = left_down_point.lon
        # While the latitude of lat_sum is lower or equal than the final point latitude
        while (lat_sum <= final_point.lat):
            # While the longitude of lon_sum is lower or equal than the final point longitude
            while (lon_sum <= final_point.lon):
                # Creates the diagonal point
                diagonal_point = diagonal_point_45(
                    distance, lat_sum, lon_sum)
                # Creates the polygon from the diagonal point and the left_down_point
                poli_grid = create_polygon(left_down_point, diagonal_point)
                # Set the lon_sum as the diagonal point longitude
                lon_sum = diagonal_point.lon
                # Set the next left_down_point with the lat_sum and the lon_sum
                left_down_point = Point(lat_sum, lon_sum)
                # Add the polygon to the grid list
                grid.append(poli_grid)
            # Set the lat_sum as the diagonal point latitude
            lat_sum = diagonal_point.lat
            # restart the lon_sum as the longitude of start_point
            lon_sum = start_point.lon
    print("Grid finished")
    print("Grid size", len(grid))
    # Returns the grid
    return grid


def grid(lat_p1: float, long_p1: float, lat_p2: float, long_p2: float, distance_arg: float | None) -> list[list[Point]]:
    """Function to create a grid of poligons that divides a geographical area in 
    small áreas of optimal size to make web scrapping on AirBnb, each poligon in 
    the grid has four points. Returns a list of Poligons.

    Args:
        lat_p1 (float): Latitude of the first point (right up)
        long_p1 (float): Longitude of the first point (right up)
        lat_p2 (float): Latitude of the second point (left down)
        long_p2 (float): Longitude of the second point (left down)
        distance_arg (float| None): Distance in diagonal between points (Optional)

    Returns:
        list[list[Point]]: A list poligons which composes the geographical grid.
    """
    global ideal_distance_meters
    # If the distance argument is not None then ideal_distance_meters is the argument
    if distance_arg is not None:
        ideal_distance_meters = distance_arg
    # Else, the ideal distance in meters is 1040
    else:
        ideal_distance_meters = 1040
    # Defines the entry point
    # latitude_A = 6.381369832596721
    # longitude_A = -75.45689986538054
    point_a = Point(lat_p1, long_p1)

    # latitude_B = 6.082295189347453
    # longitude_B = -75.70019021160994
    point_b = Point(lat_p2, long_p2)

    # Calculate the distance between the tow entry points
    distance_points = get_distance_meters(point_a, point_b)
    print("DISTANCE BETWEEN POINTS: ", distance_points)

    # Calculates the squared side and pythagoras of the ideal distance
    square_side = math.sqrt((ideal_distance_meters**2)/2)
    square_pythagoras = math.sqrt(square_side**2+square_side**2)
    print(square_side, square_pythagoras)

    # Starts the grid list
    grid = []
    # Creates a polygon of the original points
    polygon_points = create_polygon(point_a, point_b)
    # If the distance between entry points is greater than ideal distance
    if distance_points > ideal_distance_meters:
        # If the distance is less than double ideal distance
        if distance_points < ideal_distance_meters*2:
            """ CASE OF LITTLE GRIDS """
            # Creates a grid of 2x2, using the average coordinates
            lat_avg = (point_a.lat+point_b.lat)/2
            lon_avg = (point_a.lon+point_b.lon)/2
            pol1 = create_polygon(Point(lat_avg, lon_avg), point_b)
            pol2 = create_polygon(Point(lat_avg, point_a.lon),
                                  Point(point_b.lat, lon_avg))
            pol3 = create_polygon(Point(point_a.lat, lon_avg),
                                  Point(lat_avg, point_b.lon))
            pol4 = create_polygon(point_a, Point(lat_avg, lon_avg))
            # return the 4 polygons as the grid
            grid = [pol1, pol2, pol3, pol4]
        # Else, if the distance is bigger than the ideal distance
        else:
            # If the distance is bigger on each axis greater zero
            if ((get_distance_meters(point_a, polygon_points["left_up"]) > 0) and
                    (get_distance_meters(point_a, polygon_points["right_down"]) > 0)):
                """ CASE OF BIG GRIDS"""
                print("BIG DISTANCE")
                # Creates the grid with a size of square_side
                grid = create_grid(polygon_points, square_side)
    # Else return one polygon of the entry points
    else:
        grid = [polygon_points]

    print("GRID SIZE: ", len(grid))
    return grid
