#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import math
import coor_utils
import pyproj
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point, LineString, LinearRing
from shapely.ops import unary_union

if __name__ == '__main__':
    # 获取计算地块内农机作业面积时必须的一些参数

    # 农机轨迹数据
    track_json_path = "./xinxiang_chongming_track.json"
    with open(track_json_path, 'r', encoding='utf-8') as f:
        track_geojson_data = json.load(f)

    # 地块边界数据
    field_json_path = "./chongming_field.json"
    with open(field_json_path, 'r', encoding='utf-8') as f:
        field_geojson_data = json.load(f)

    # 农具作业幅宽
    width = 2.3
    # 农具深耕阈值
    deep_depth = 15.0
    # 农具浅耕阈值
    shallow_depth = 12.0

    # ---------------------------------------------------#
    # 农具作业幅宽的一半长度
    half_width = width / 2

    # 遍历轨迹并获取坐标
    track_points_raw_list = []
    lons_raw_list = []
    for point in track_geojson_data:
        lon = point['lng']
        lat = point['lat']
        depth = point['deep']
        track_points_raw_list.append(tuple((lon, lat, depth)))
        lons_raw_list.append(lon)

    # 遍历地块所有要素并获取坐标
    field_points = []
    for feature in field_geojson_data['features']:
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

    # 定义转换器，从 WGS84 坐标系转换到 UTM 坐标系
    # 判断轨迹坐标中位数所处 UTM 投影带
    mid_lon = coor_utils.get_median(lons_raw_list)
    utm_proj = coor_utils.check_utm(mid_lon)

    wgs84 = pyproj.CRS('EPSG:4326')
    utm = pyproj.CRS(utm_proj)
    transformer = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True)

    # ---------------------------------------------------#
    #   计算地块总面积
    # ---------------------------------------------------#
    # 将经纬度坐标转换为 UTM 坐标系下的坐标
    field_points_utm = [transformer.transform(poi[0], poi[1]) for poi in field_points]
    # 点连接成线
    field_line = LinearRing(field_points_utm)
    # 将线转换为 GeoDataFrame
    field_gdf = gpd.GeoDataFrame(geometry=[field_line])

    # 计算点集合围成的多边形的面积
    field_poly = Polygon(field_line)
    field_area = field_poly.area
    print(f'Field area: {field_area / 2000 * 3:.4f}')

    # ---------------------------------------------------#
    #   计算农机运动总面积(包含深耕、浅耕和无动作面积)
    # ---------------------------------------------------#
    # 将经纬度坐标转换为 UTM 坐标系下的坐标
    total_points_utm = [transformer.transform(poi[0], poi[1]) for poi in track_points_filter_list]
    # 点连接成线
    total_line = LineString(total_points_utm)
    # 将线转换为 GeoDataFrame
    track_gdf = gpd.GeoDataFrame(geometry=[total_line])

    # 创建线的缓冲区
    total_buffered = total_line.buffer(half_width)
    # 计算点集合围成的多边形的面积
    total_poly = Polygon(total_buffered)
    total_area = total_poly.area - (math.pi * half_width ** 2)
    print(f'Activity area: {total_area / 2000 * 3:.4f}')

    # ---------------------------------------------------#
    #   计算农机深耕、浅耕、耕作总（除去重叠面积）面积
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
        if len(dl) == 1:
            deep_point = Point(dl)
            deep_buffered = deep_point.buffer(half_width)
        if len(dl) > 1:
            deep_line = LineString(dl)
            deep_buffered = deep_line.buffer(half_width)
        deep_poly = Polygon(deep_buffered)
        deep_poly_list.append(deep_poly)
        total_poly_list.append(deep_poly)
        deep_area = deep_poly.area
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
        if len(sl) == 1:
            shallow_point = Point(sl)
            shallow_buffered = shallow_point.buffer(half_width)
        if len(sl) > 1:
            shallow_line = LineString(sl)
            shallow_buffered = shallow_line.buffer(half_width)
        shallow_poly = Polygon(shallow_buffered)
        shallow_poly_list.append(shallow_poly)
        total_poly_list.append(shallow_poly)
        shallow_area = shallow_poly.area
        shallow_total_area = shallow_total_area + shallow_area

    # ---------------------------------------------------#
    # 计算深耕多边形的并集面积
    union_deep_polygon = unary_union(deep_poly_list)
    # cultivation_deep_area = union_deep_polygon.area - (math.pi * half_width ** 2) * len(deep_poly_list)
    cultivation_deep_area = union_deep_polygon.area
    print(f'Deep cultivation area: {cultivation_deep_area / 2000 * 3:.4f}')

    # 计算浅耕多边形的并集面积
    union_shallow_polygon = unary_union(shallow_poly_list)
    # cultivation_shallow_area = union_shallow_polygon.area - (math.pi * half_width ** 2) * len(shallow_poly_list)
    cultivation_shallow_area = union_shallow_polygon.area
    print(f'Shallow cultivation area: {cultivation_shallow_area / 2000 * 3:.4f}')

    # 计算总作业多边形的并集面积
    union_total_polygon = unary_union(total_poly_list)
    # cultivation_total_area = union_total_polygon.area - (math.pi * half_width ** 2) * len(total_poly_list)
    cultivation_total_area = union_total_polygon.area
    print(f'Total cultivation area: {cultivation_total_area / 2000 * 3:.4f}')

    # 计算重复作业面积
    deep_shallow_total_area = deep_total_area + shallow_total_area
    overlap_total_area = deep_shallow_total_area - cultivation_total_area
    print(f'Overlap cultivation area: {overlap_total_area / 2000 * 3:.4f}')

    # ---------------------------------------------------#
    #   绘制多边形和结果
    # ---------------------------------------------------#
    fig, ax = plt.subplots()
    track_gdf.plot(ax=ax, color='black', linewidth=0.5)
    field_gdf.plot(ax=ax, color='orange', linewidth=1.0)
    # ax.add_patch(plt.Polygon(total_poly.exterior, color='blue', alpha=0.5))
    ax.scatter(*zip(*total_points_utm), color='red', s=5, zorder=1)
    for sl in shallow_lines_poi:
        if len(sl) == 1:
            shallow_point = Point(sl)
            shallow_buffered = shallow_point.buffer(half_width)
        if len(sl) > 1:
            shallow_line = LineString(sl)
            shallow_buffered = shallow_line.buffer(half_width)
        shallow_poly = Polygon(shallow_buffered)
        ax.add_patch(plt.Polygon(shallow_poly.exterior, color='blue', alpha=0.5))
        ax.scatter(*zip(*sl), color='blue', s=5, zorder=2)
    for dl in deep_lines_poi:
        if len(dl) == 1:
            deep_point = Point(dl)
            deep_buffered = deep_point.buffer(half_width)
        if len(dl) > 1:
            deep_line = LineString(dl)
            deep_buffered = deep_line.buffer(half_width)
        deep_poly = Polygon(deep_buffered)
        ax.add_patch(plt.Polygon(deep_poly.exterior, color='green', alpha=0.5))
        ax.scatter(*zip(*dl), color='green', s=5, zorder=2)
    ax.set_aspect('equal', 'box')
    ax.set_title(f'Total cultivation area: {cultivation_total_area / 2000 * 3:.4f}')
    plt.show()
