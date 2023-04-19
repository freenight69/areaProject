#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import argparse
import cal_area as ca

"""
python run_area.py --track_data track_json_data --field_data field_json_data --width 2.3 --deep_depth 15.0 --shallow_depth 12.0
"""

# 获取计算地块内农机作业面积时必须的一些参数
# 打开轨迹 GeoJSON 文件并读取内容
track_json_path = "./xinxiang_chongming_track.json"
with open(track_json_path, 'r', encoding='utf-8') as f:
    track_geojson_data = json.load(f)

# 打开地块 GeoJSON 文件并读取内容
field_json_path = "./chongming_field.json"
with open(field_json_path, 'r', encoding='utf-8') as f:
    field_geojson_data = json.load(f)

parser = argparse.ArgumentParser(description='Calculate operation area agricultural machinery of from track data')
parser.add_argument('--track_data', default=track_geojson_data, help='Track data of agricultural machinery')
parser.add_argument('--field_data', default=field_geojson_data, help='Field json data')
parser.add_argument('--width', type=float, default=2.3, help='Width of agricultural implement')
parser.add_argument('--deep_depth', type=float, default=15.0, help='Deep tillage depth')
parser.add_argument('--shallow_depth', type=float, default=12.0, help='Shallow tillage depth')

opt = parser.parse_args()

if __name__ == '__main__':
    track_length, field_area, total_area, cultivation_deep_area, cultivation_shallow_area, cultivation_total_area, overlap_total_area = ca.track_area(
        opt.track_data, opt.field_data, opt.width, opt.deep_depth, opt.shallow_depth)
    print(f'Track length (km): {track_length:.4f}')
    print(f'Activity area (mu): {total_area:.4f}')
    print(f'Field area (mu): {field_area:.4f}')
    print(f'Deep cultivation area (mu): {cultivation_deep_area:.4f}')
    print(f'Shallow cultivation area (mu): {cultivation_shallow_area:.4f}')
    print(f'Total cultivation area (mu): {cultivation_total_area:.4f}')
    print(f'Overlap cultivation area (mu): {overlap_total_area:.4f}')
