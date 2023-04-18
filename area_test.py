#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import cal_area as ca

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

    field_area, total_area, cultivation_deep_area, cultivation_shallow_area, cultivation_total_area, overlap_total_area = ca.track_area(
        track_geojson_data, field_geojson_data, width, deep_depth, shallow_depth)
    print(f'Field area: {field_area:.4f}')
    print(f'Activity area: {total_area:.4f}')
    print(f'Deep cultivation area: {cultivation_deep_area:.4f}')
    print(f'Shallow cultivation area: {cultivation_shallow_area:.4f}')
    print(f'Total cultivation area (without overlap): {cultivation_total_area:.4f}')
    print(f'Overlap cultivation area: {overlap_total_area:.4f}')
