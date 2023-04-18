#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 计算中位数
def get_median(data):
    """
    根据农机终端轨迹计算农机作业面积

    :param data: 农机轨迹数据
    :return: 地块面积, 轨迹覆盖面积, 深耕作业面积, 浅耕作业面积, 总作业面积(不包括重复作业), 重复作业面积
    """
    data.sort()
    half = len(data) // 2
    return (data[half] + data[~half]) / 2


def check_utm(lon):
    """
    根据农机终端轨迹计算农机作业面积

    :param lon: 农机轨迹数据
    :return: 地块面积, 轨迹覆盖面积, 深耕作业面积, 浅耕作业面积, 总作业面积(不包括重复作业), 重复作业面积
    """
    if 73.62 <= lon < 76.50:
        return 'EPSG:4513'
    elif 73.50 <= lon < 79.50:
        return 'EPSG:4514'
    elif 79.50 <= lon < 82.50:
        return 'EPSG:4515'
    elif 82.50 <= lon < 85.50:
        return 'EPSG:4516'
    elif 82.50 <= lon < 85.50:
        return 'EPSG:4516'
    elif 85.50 <= lon < 88.50:
        return 'EPSG:4517'
    elif 88.50 <= lon < 91.50:
        return 'EPSG:4518'
    elif 91.50 <= lon < 94.50:
        return 'EPSG:4519'
    elif 94.50 <= lon < 97.50:
        return 'EPSG:4520'
    elif 97.50 <= lon < 100.50:
        return 'EPSG:4521'
    elif 100.50 <= lon < 103.50:
        return 'EPSG:4522'
    elif 103.50 <= lon < 106.50:
        return 'EPSG:4523'
    elif 106.50 <= lon < 109.50:
        return 'EPSG:4524'
    elif 109.50 <= lon < 112.50:
        return 'EPSG:4525'
    elif 112.50 <= lon < 115.50:
        return 'EPSG:4526'
    elif 115.50 <= lon < 118.50:
        return 'EPSG:4527'
    elif 118.50 <= lon < 121.50:
        return 'EPSG:4528'
    elif 121.50 <= lon < 124.50:
        return 'EPSG:4529'
    elif 124.50 <= lon < 127.50:
        return 'EPSG:4530'
    elif 127.50 <= lon < 130.50:
        return 'EPSG:4531'
    elif 130.50 <= lon < 133.50:
        return 'EPSG:4532'
    elif 130.50 <= lon <= 134.77:
        return 'EPSG:4533'
    else:
        raise ValueError("ERROR!!! Track data is beyond the boundary of China")
