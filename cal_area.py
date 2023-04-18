#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import pyproj
from shapely.geometry import Polygon, Point, LineString, LinearRing
from shapely.ops import unary_union


def track_area(track_data, field_data, width, deep_depth, shallow_depth):
    """
    根据农机终端轨迹计算农机作业面积

    :param track_data: 农机轨迹数据
    :param field_data: 地块边界数据
    :param width: 农具作业幅宽
    :param deep_depth: 农具深耕阈值
    :param shallow_depth: 农具浅耕阈值
    :return: 地块面积, 轨迹覆盖面积, 深耕作业面积, 浅耕作业面积, 总作业面积(不包括重复作业), 重复作业面积
    """
    # 农具作业幅宽的一半长度
    half_width = width / 2.0

    # ---------------------------------------------------#
    #   1. 只保留地块范围内轨迹
    # ---------------------------------------------------#
    # 遍历轨迹并获取坐标
    track_points_raw_list = []
    for point in track_data:
        lon = point['lng']
        lat = point['lat']
        depth = point['deep']
        track_points_raw_list.append(tuple((lon, lat, depth)))

    # 遍历地块所有要素并获取坐标
    field_points = []
    for feature in field_data['features']:
        geom = feature['geometry']
        for point in geom['rings'][0]:
            field_points.append(tuple(point))
    # 创建地块多边形对象
    field_polygon = Polygon(field_points)

    track_points_filter_list = []
    for poi in track_points_raw_list:
        track_poi = Point(poi[0], poi[1])
        # 判断点是否在GeoJSON矢量范围内
        if field_polygon.contains(track_poi):
            track_points_filter_list.append(poi)

    # ---------------------------------------------------#
    #   2. 坐标系转换，由地理坐标系转换为投影坐标系
    # ---------------------------------------------------#
    # 定义转换器，从 WGS84 坐标系转换到 UTM 坐标系
    wgs84 = pyproj.CRS('EPSG:4326')
    utm = pyproj.CRS('EPSG:4529')
    transformer = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True)

    # ---------------------------------------------------#
    #   3. 计算地块总面积
    # ---------------------------------------------------#
    # 将经纬度坐标转换为 UTM 坐标系下的坐标
    field_points_utm = [transformer.transform(poi[0], poi[1]) for poi in field_points]
    # 点连接成线
    field_line = LinearRing(field_points_utm)

    # 计算点集合围成的多边形的面积
    field_poly = Polygon(field_line)
    field_area = field_poly.area / 2000 * 3

    # ---------------------------------------------------#
    #   4. 计算农机运动总面积(包含深耕、浅耕和无动作面积)
    # ---------------------------------------------------#
    # 将经纬度坐标转换为 UTM 坐标系下的坐标
    total_points_utm = [transformer.transform(poi[0], poi[1]) for poi in track_points_filter_list]
    # 点连接成线
    total_line = LineString(total_points_utm)

    # 创建线的缓冲区
    total_buffered = total_line.buffer(half_width)
    # 计算点集合围成的多边形的面积
    total_poly = Polygon(total_buffered)
    total_area = (total_poly.area - (math.pi * half_width ** 2)) / 2000 * 3

    # ---------------------------------------------------#
    #   5. 计算农机深耕、浅耕、耕作总（除去重叠面积）面积
    # ---------------------------------------------------#
    # 定义耕作总面积
    total_poly_list = []
    # 定义深耕总面积
    deep_poly_list = []
    # 定义浅耕总面积
    shallow_poly_list = []

    # ---------------------------------------------------#
    # 定义一个存储做深耕活动线段点的数组
    deep_lines_poi = []
    # 定义一个存储单条深耕活动线段点的数组
    deep_temp_poi = []
    for i in range(len(track_points_filter_list)):
        # 将经纬度坐标转换为 UTM 坐标系下的坐标
        lon_utm, lat_utm = transformer.transform(track_points_filter_list[i][0], track_points_filter_list[i][1])
        # 判断deep大于deep_depth，认为是做深耕活动
        if track_points_filter_list[i][2] >= deep_depth:
            deep_temp_poi.append(tuple((lon_utm, lat_utm)))
            if track_points_filter_list[i + 1][2] < deep_depth:
                deep_lines_poi.append(deep_temp_poi)
                deep_temp_poi = []
                continue

    # 定义深耕总面积
    deep_total_area = 0
    for dl in deep_lines_poi:
        if len(dl) > 1:
            deep_line = LineString(dl)
            deep_buffered = deep_line.buffer(half_width)
            deep_poly = Polygon(deep_buffered)
            deep_poly_list.append(deep_poly)
            total_poly_list.append(deep_poly)
            deep_area = deep_poly.area - (math.pi * half_width ** 2)
            deep_total_area = deep_total_area + deep_area

    # ---------------------------------------------------#
    # 定义一个存储做浅耕活动线段点的数组
    shallow_lines_poi = []
    # 定义一个存储单条浅耕活动线段点的数组
    shallow_temp_poi = []
    for i in range(len(track_points_filter_list)):
        # 将经纬度坐标转换为 UTM 坐标系下的坐标
        lon_utm, lat_utm = transformer.transform(track_points_filter_list[i][0], track_points_filter_list[i][1])
        # 判断shallow_depth<=deep<deep_depth，认为是做浅耕活动
        if shallow_depth <= track_points_filter_list[i][2] < deep_depth:
            shallow_temp_poi.append(tuple((lon_utm, lat_utm)))
            if track_points_filter_list[i + 1][2] < shallow_depth or track_points_filter_list[i + 1][2] >= deep_depth:
                shallow_lines_poi.append(shallow_temp_poi)
                shallow_temp_poi = []
                continue

    # 定义浅耕总面积
    shallow_total_area = 0
    for sl in shallow_lines_poi:
        if len(sl) > 1:
            shallow_line = LineString(sl)
            shallow_buffered = shallow_line.buffer(half_width)
            shallow_poly = Polygon(shallow_buffered)
            shallow_poly_list.append(shallow_poly)
            total_poly_list.append(shallow_poly)
            shallow_area = shallow_poly.area - (math.pi * half_width ** 2)
            shallow_total_area = shallow_total_area + shallow_area

    # ---------------------------------------------------#
    # 计算深耕多边形的并集面积
    union_deep_polygon = unary_union(deep_poly_list)
    cultivation_deep_area = union_deep_polygon.area / 2000 * 3

    # 计算浅耕多边形的并集面积
    union_shallow_polygon = unary_union(shallow_poly_list)
    cultivation_shallow_area = union_shallow_polygon.area / 2000 * 3

    # 计算总作业多边形的并集面积
    union_total_polygon = unary_union(total_poly_list)
    cultivation_total_area = union_total_polygon.area / 2000 * 3

    # 计算重复作业面积
    deep_shallow_total_area = deep_total_area + shallow_total_area
    overlap_total_area = (deep_shallow_total_area - union_total_polygon.area) / 2000 * 3

    print(field_area, total_area, cultivation_deep_area, cultivation_shallow_area, cultivation_total_area,
          overlap_total_area)

    return field_area, total_area, cultivation_deep_area, cultivation_shallow_area, cultivation_total_area, \
        overlap_total_area
