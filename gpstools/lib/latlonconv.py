"""
Copyright (c) 2014-2015 Gen Del Raye
Copyright (c) 2015 Ryan Vennell

This is a derivative, forked from the original work by:
Gen Del Raye <gdelraye@hawaii.edu> and located at:
https://pypi.python.org/pypi/LatLon

Licensed under the GPLv3: http://www.gnu.org/licenses/gpl-3.0.html
"""
import re
import abc

'''
Methods for representing geographic coordinates (latitude and longitude)
Features:
    Convert lat/lon strings from any format into a LatLon object
    Automatically store decimal degrees, decimal minutes, and degree, minute, second
      information in a LatLon object
    Output lat/lon information into a formatted string
    Project lat/lon coordinates into some other proj projection
    Calculate distances between lat/lon pairs using either the FAI or WGS84 approximation
Written July 22, 2014
Author: Gen Del Raye
'''

def compare(a, b):
    return (a > b) - (a < b)

class GeoCoord:
    '''
    Abstract class representing geographic coordinates (i.e. latitude or longitude)
    Not meant to be used directly - access through Subclasses Latitude() and Longitude()
    '''
    __metaclass__ = abc.ABCMeta

    def __init__(self, degree = 0, minute = 0, second = 0):
        '''
        Initialize a GeoCoord object
        Inputs:
            degree (scalar) - integer or decimal degrees. If decimal degrees are given (e.g. 5.83),
              the fractional values (0.83) will be added to the minute and second variables.
            minute (scalar) - integer or decimal minutes. If decimal minutes are given (e.g. 49.17),
              the fractional values (0.17) will be added to the second variable.
            second (scalar) - decimal minutes.
        '''
        self.degree = float(degree)
        self.minute = float(minute)
        self.second = float(second)
        self._update() # Clean up each variable and make them consistent

    def set_minute(self, minute):
        self.minute = float(minute)

    def set_second(self, second):
        self.second = float(second)

    def set_degree(self, degree):
        self.degree = float(degree)

    @staticmethod
    def _calc_decimaldegree(degree, minute, second):
        '''
        Calculate decimal degree form degree, minute, second
        '''
        return degree + minute/60. + second/3600.

    @staticmethod
    def _calc_degreeminutes(decimal_degree):
        '''
        Calculate degree, minute second from decimal degree
        '''
        sign = compare(decimal_degree, 0) # Store whether the coordinate is negative or positive
        decimal_degree = abs(decimal_degree)
        degree = decimal_degree//1 # Truncate degree to be an integer
        decimal_minute = (decimal_degree - degree)*60. # Calculate the decimal minutes
        minute = decimal_minute//1 # Truncate minute to be an integer
        second = (decimal_minute - minute)*60. # Calculate the decimal seconds
        # Finally, re-impose the appropriate sign
        degree = degree*sign
        minute = minute*sign
        second = second*sign
        return (degree, minute, decimal_minute, second)

    def _update(self):
        '''
        Given degree, minute, and second information, clean up the variables and make them
        consistent (for example, if minutes > 60, add extra to degrees, or if degrees is
        a decimal, add extra to minutes).
        '''
        self.decimal_degree = self._calc_decimaldegree(self.degree, self.minute, self.second)
        self.degree, self.minute, self.decimal_minute, self.second = self._calc_degreeminutes(self.decimal_degree)

    @abc.abstractmethod
    def get_hemisphere(self):
        '''
        Dummy method, used in child classes such as Latitude and Longitude
        '''
        pass

    @abc.abstractmethod
    def set_hemisphere(self):
        '''
        Dummy method, used in child classes such as Latitude and Longitude
        '''
        pass

    def to_string(self, format_str):
        '''
        Output lat, lon coordinates as string in chosen format
        Inputs:
            format (str) - A string of the form A%B%C where A, B and C are identifiers.
              Unknown identifiers (e.g. ' ', ', ' or '_' will be inserted as separators
              in a position corresponding to the position in format.
        Examples:
            >> palmyra = LatLon(5.8833, -162.0833)
            >> palmyra.to_string('D') # Degree decimal output
            ('5.8833', '-162.0833')
            >> palmyra.to_string('H% %D')
            ('N 5.8833', 'W 162.0833')
            >> palmyra.to_string('d%_%M')
            ('5_52.998', '-162_4.998')
        '''
        format2value = {'H': self.get_hemisphere(),
                        'M': "{:.3f}".format(abs(self.decimal_minute)),
                        'm': int(abs(self.minute)),
                        'd': int(self.degree),
                        'D': "{:.5f}".format(self.decimal_degree),
                        'S': "{:.1f}".format(abs(self.second))}
        format_elements = format_str.split('%')
        coord_list = [str(format2value.get(element, element)) for element in format_elements]
        coord_str = ''.join(coord_list)
        if 'H' in format_elements: # No negative values when hemispheres are indicated
            coord_str = coord_str.replace('-', '')
        return coord_str

    def __int__(self):
        return self.degree

    def __float__(self):
        return self.decimal_degree

    def __str__(self):
        return str(self.decimal_degree)

class Latitude(GeoCoord):
    '''
    Coordinate object specific for latitude coordinates
    '''
    def get_hemisphere(self):
        '''
        Returns the hemisphere identifier for the current coordinate
        '''
        if self.decimal_degree < 0: return 'S'
        else: return 'N'

    def set_hemisphere(self, hemi_str):
        '''
        Given a hemisphere identifier, set the sign of the coordinate to match that hemisphere
        '''
        if hemi_str == 'S':
            self.degree = abs(self.degree)*-1
            self.minute = abs(self.minute)*-1
            self.second = abs(self.second)*-1
            self._update()
        elif hemi_str == 'N':
            self.degree = abs(self.degree)
            self.minute = abs(self.minute)
            self.second = abs(self.second)
            self._update()
        else:
            raise ValueError('Hemisphere identifier for latitudes must be N or S')

class Longitude(GeoCoord):
    '''
    Coordinate object specific for longitude coordinates
    Langitudes outside the range -180 to 180 (i.e. those reported in the range 0 to 360) will
    automatically be converted to 0 to 360 to ensure that all operations such as hemisphere
    assignment work as expected. To report in the range 0 to 360, use method range360()
    '''
    def __init__(self, degree = 0, minute = 0, second = 0):
        super(Longitude, self).__init__(degree, minute, second) # Initialize the GeoCoord
        decimal_degree = self.range180() # Make sure that longitudes are reported in the range -180 to 180
        self.degree, self.minute, self.decimal_minute, self.second = self._calc_degreeminutes(decimal_degree)
        self._update()

    def range180(self):
        '''
        Report longitudes using the range -180 to 180.
        '''
        return ((self.decimal_degree + 180)%360) - 180

    def get_hemisphere(self):
        '''
        Returns the hemisphere identifier for the current coordinate
        '''
        if self.decimal_degree < 0: return 'W'
        else: return 'E'

    def set_hemisphere(self, hemi_str):
        '''
        Given a hemisphere identifier, set the sign of the coordinate to match that hemisphere
        '''
        if hemi_str == 'W':
            self.degree = abs(self.degree)*-1
            self.minute = abs(self.minute)*-1
            self.second = abs(self.second)*-1
            self._update()
        elif hemi_str == 'E':
            self.degree = abs(self.degree)
            self.minute = abs(self.minute)
            self.second = abs(self.second)
            self._update()
        else:
            raise ValueError('Hemisphere identifier for longitudes must be E or W')

def string2geocoord(coord_str, coord_class, format_str = 'D'):
    '''
    Create a GeoCoord object (e.g. Latitude or Longitude) from a string.
    Inputs:
        coord_str (str) - a string representation of a geographic coordinate (e.g. '5.083 N'). Each
          section of the string must be separated by some kind of a separator character ('5.083N' is
          invalid).
        coord_class (class) - a class inheriting from GeoCoord that includes a set_hemisphere method.
          Can be either Latitude or Longitude
        format_str (str) - a string representation of the sections of coord_str. Possible letter values
        correspond to the keys of the dictionary format2value, where
              'H' is a hemisphere identifier (e.g. N, S, E or W)
              'D' is a coordinate in decimal degrees notation
              'd' is a coordinate in degrees notation
              'M' is a coordinate in decimal minutes notaion
              'm' is a coordinate in minutes notation
              'S' is a coordinate in seconds notation
              Any other characters (e.g. ' ' or ', ') will be treated as a separator between the above components.
          All components should be separated by the '%' character. For example, if the coord_str is
          '5, 52, 59.88_N', the format_str would be 'd%, %m%, %S%_%H'
    Returns:
        GeoCoord object initialized with the coordinate information from coord_str
    '''
    new_coord = coord_class()
    # Dictionary of functions for setting variables in the coordinate class:
    format2value = {'H': new_coord.set_hemisphere,
                    'M': new_coord.set_minute,
                    'm': new_coord.set_minute,
                    'd': new_coord.set_degree,
                    'D': new_coord.set_degree,
                    'S': new_coord.set_second}
    if format_str[0] == 'H':
        ''' Having the hemisphere identifier at the beginning is problematic for ensuring that
        the final coordinate value will be negative. Instead, change the identifier and the
        format string so that the hemisphere is identified at the end:'''
        new_coord_start = re.search('\d', coord_str).start() # Find the beginning of the coordinate
        new_format_start = re.search('[a-gi-zA-GI-Z]', format_str).start() # Find the first non-hemisphere identifier
        format_str = '% %'.join((format_str[new_format_start:], format_str[0])) # Move hemisphere identifier to the back
        coord_str = ' '.join((coord_str[new_coord_start:], coord_str[0])) # Move hemisphere identifier to the back
    format_elements = format_str.split('%')
    separators = [sep for sep in format_elements if sep not in format2value.keys()] # E.g. ' ', '_' or ', ' characters
    separators.append('%') # Dummy separator for the final part of the coord_str
    formatters = [form for form in format_elements if form in format2value.keys()] # E.g. 'D', 'm', or 'S' characters
    for form, sep in zip(formatters, separators):
        coord_elements = coord_str.split(sep)
        format2value[form](coord_elements[0]) # Set the coordinate variable (e.g. 'self.degree' with the coordinate substring (e.g. '5')
        coord_str = sep.join(coord_elements[1:]) # Get rid of parts of the substring that have already been done
    new_coord._update() # Change all of the variables in the coordinate class so they are consistent with each other
    return new_coord

class LatLon:
    '''
    Object representing lat/lon pairs
    '''
    def __init__(self, lat, lon, name = None):
        '''
        Input:
            lat (class instance or scalar) - an instance of class Latitude or a scalar. A Latitude object
              can be instantiated directly in the __init__ call for example by calling LatLon(Latitude(5.8),
              Longitude(162.5)). If lat is specified as a scalar, the scalar will be assumed to be in
              decimal degrees.
            lon (class instance or scalar) - an instance of class Longitude or a scalar. If lat is
              specified as a scalar, the scalar will be assumed to be in decimal degrees.
            name (str) - an identifier
        '''
        try:
            if lat.type() == 'GeoCoord':
                self.lat = lat
            else:
                raise AttributeError
        except AttributeError:
            self.lat = Latitude(lat)
        try:
            if lon.type() == 'GeoCoord':
                self.lon = lon
            else:
                raise AttributeError
        except AttributeError:
            self.lon = Longitude(lon)
        self.name = name

    def to_string(self, formatter = 'D'):
        '''
        Return string representation of lat and lon as a 2-element tuple
        using the format specified by formatter
        '''
        return (self.lat.to_string(formatter), self.lon.to_string(formatter))

def string2latlon(lat_str, lon_str, format_str):
    '''
    Create a LatLon object from a pair of strings.
    Inputs:
        lat_str (str) - string representation of a latitude (e.g. '5 52 59.88 N')
        lon_str (str) - string representation of a longitude (e.g. '162 4 59.88 W')
        format_str (str) - format in which the coordinate strings are given (e.g.
          for the above examples this would be 'd% %m% %S% %H'). See function
          string2geocoord for a detailed explanation on how to specify formats.
    Returns:
        A LatLon object initialized with coordinate data from lat_str and lon_str
    '''
    lat = string2geocoord(lat_str, Latitude, format_str)
    lon = string2geocoord(lon_str, Longitude, format_str)
    new_latlon = LatLon(lat = lat, lon = lon)
    return new_latlon
