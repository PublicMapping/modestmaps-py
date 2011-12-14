"""
>>> w = Provider('http://localhost:8080/geoserver/gwc/service/wms')
>>> w.server
'http://localhost:8080/geoserver/wms'
>>> w.wms
'?LAYERS=0%2C1&SERVICE=WMS&WIDTH=256&FORMAT=image%2Fpng&REQUEST=GetMap&HEIGHT=256&SRS=EPSG%3A4326&VERSION=1.1.1'
>>> w.getTileUrls(Coordinate(0, 0, 20))
['http://localhost:8080/geoserver/wms?LAYERS=0%2C1&SERVICE=WMS&WIDTH=256&FORMAT=image%2Fpng&REQUEST=GetMap&HEIGHT=256&SRS=EPSG%3A4326&VERSION=1.1.1&BBOX=-180.000000,180.021231,-179.999657,180.021574']
"""

from Core import Coordinate
from Providers import IMapProvider
from Geo import Transformation, LinearProjection, MercatorProjection
from urllib import urlencode
from copy import copy
import math

class Provider(IMapProvider):
    _PARAMS = {
        'LAYERS': '0,1',
        'FORMAT': 'image/png',
        'VERSION': '1.1.1',
        'SERVICE': 'WMS',
        'REQUEST': 'GetMap',
        'SRS': 'EPSG:4326',
        'WIDTH': 256,
        'HEIGHT': 256
    }

    def __init__(self, server, params=None):
        self.params = copy(Provider._PARAMS)

        if not params is None:
            self.params.update(params)

        if 'SLD_BODY' in self.params:
            self.postData = self.params['SLD_BODY']
            del self.params['SLD_BODY']
        else:
            self.postData = None

        self.server = server.replace('gwc/service/','')

        self.wms = '?' + urlencode(self.params)

        if 'SRS' in self.params and self.params['SRS'] == 'EPSG:4326':
            self.projection = LinearProjection(20, Transformation(166886.05360752725, 0, 524288, 0, -166866.05360752725, 524288))
        else:
            self.projection = MercatorProjection(26, Transformation(1.068070779e7, 0, 3.355443185e7, 0, -1.068070890e7, 3.355443057e7))

    def getTileUrls(self, coord):
        #worldSize = math.pow(coord.zoom, 2);
        #if coord.row < 0 or coord.row > worldSize:
        #    print 'WARNING: outside coordinates. Row:',coord.row,', WorldSize:',worldSize
        #    return []

        sourceCoord = self.sourceCoordinate(coord)
        ll = sourceCoord.down()
        ur = sourceCoord.right()

        bbox = ''
        if 'SRS' in self.params and self.params['SRS'] == 'EPSG:4326':
            ll_loc = self.coordinateLocation(ll)
            ur_loc = self.coordinateLocation(ur)
            bbox = '&BBOX=%f,%f,%f,%f' % (ll_loc.lon, ll_loc.lat, ur_loc.lon, ur_loc.lat)
        else:
            qwidth = 20037508.34;
            mzoom = math.log(2*qwidth) / math.log(2)

            ll = ll.zoomTo(mzoom)
            ur = ur.zoomTo(mzoom)

            bbox = '&BBOX=%f,%f,%f,%f' % (
                ll.column - qwidth,
                qwidth - ll.row,
                ur.column - qwidth,
                qwidth - ur.row
            )

        return ['%s%s%s' % (self.server, self.wms, bbox)]

    def tileWidth(self):
        return self.params['WIDTH']

    def tileHeight(self):
        return self.params['HEIGHT']

    def getPostData(self):
        return self.postData

if __name__ == '__main__':
    import doctest
    doctest.testmod()
