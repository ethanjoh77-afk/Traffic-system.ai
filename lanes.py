import cv2
import numpy as np

# BRT lane polygon (BADILISHA HII kulingana na video yako)
BRT_ZONE = [(300,250), (900,250), (1000,600), (200,600)]

def is_inside_zone(cx, cy, zone):
    zone_np = np.array(zone, dtype=np.int32)

    return cv2.pointPolygonTest(
        zone_np,
        (cx, cy),
        False
    ) >= 0