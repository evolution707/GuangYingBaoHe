# -*- coding=utf-8 -*-
import datetime


def datetime_handle(obj):
    # datetime类型自定义序列化
    if isinstance(obj, datetime.datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(obj, datetime.date):
        return obj.strftime("%Y-%m-%d")
    else:
        raise TypeError("Unknown type")