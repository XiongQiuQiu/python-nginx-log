#!/usr/bin/python
# coding=utf-8

import sys
import xlwt
import argparse
import gzip
import datetime
import logging

reload(sys)
sys.setdefaultencoding('utf-8')


logging.basicConfig(level=logging.DEBUG)

op_name_dict = {'0': u'图标曝光',
                '1': u'点击按钮',
                '2': u'落地也加载',
                '3': u'视频展示',
                '4': u'播放完成',
                '5': u'视频主动关闭',
                '8': u'下载按钮',
                '99': u'关闭'}

os_name_dict = {'0': u'全部',
                '1': u'iphone',
                '2': u'android',
                '3': u'其他'}

area_name_dict = {'1': u'顶部',
                  '2': u'底部按钮',
                  'null': u'全部'}

class an_log(object):
    """分析记录"""
    def __init__(self, filename):
        self.filename = filename
        self.picid_value = {}  # # 一个用于存储所有pv，uv的字典

    def read_log(self):
        f = gzip.open(self.filename, 'r')
        for line in f:
            all_line = line.split()
            try:
                a_line = dict(k.split('=') for k in all_line[8].split('&'))
                # 把所有参数解析到一个字典中，key为参数名，value为参数值类似于{type:1,param:A00184}
                ip = all_line[1]  # 获取ip
                media_id = a_line['param']
                op = a_line['op']
            except:
                continue
            try:
                adsid = a_line.get('adsid', 'null')
                picid = a_line.get('picid', 'null')
                area_name = a_line.get('area', 'null')
                os = a_line.get('os', '0')
            except:
                continue
            pic = picid + media_id + adsid + op + area_name + os  # 把参数组合生成唯一键名
            if pic in  self.picid_value.keys():
                self.analysis_pv(pic)
                self.analysis_uv(pic, ip)
            else:
                self.in_value()
                self.analysis_pv(pic)
                self.analysis_uv(pic, ip)
        return self.picid_value

    def in_value(self):
        self.picid_value[pic] = {}
        self.picid_value[pic]['picid'] = picid
        self.picid_value[pic]['adsid'] = adsid
        self.picid_value[pic]['media_id'] = media_id
        self.picid_value[pic]['op'] = op_name_dict[op]
        self.picid_value[pic]['os'] = os_name_dict[os]
        self.picid_value[pic]['pv'] = 0
        self.picid_value[pic]['uv'] = 0
        self.picid_value[pic]['ip'] = set()
        self.picid_value[pic]['area'] = area_name_dict[area_name]

    def analysis_pv(self, pic,):
        self.picid_value[pic]['pv'] += 1
        return self.picid_value

    def analysis_uv(self, pic, ip):
        if ip not in self.picid_value[pic]['ip']:
            self.picid_value[pic]['uv'] += 1
            self.picid_value[pic]['ip'].add(ip)
        return self.picid_value

    def judge_line(self, line):  #判断日志类型是否为所需类型，已弃用
        s = '/index.php?'
        if s in line[8]:
            return True
        else:
            return False

    def print_for(self):
        for pic in self.picid_value:
            msg = u'媒体:' + str(self.picid_value[pic]['media_id'])+'op:' + str(self.picid_value[pic]['op'])+'adisd:' + str(
                    self.picid_value[pic]['adsid']) + 'picid:' + str(self.picid_value[pic]['picid'])+'pv:' + str(
                    self.picid_value[pic]['pv']) + 'uv:' + str(self.picid_value[pic]['uv'])
            logging.info(msg)

    def write_excel(self, excel_name):
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('toolbar')
        cl_name = [u'媒体', 'op', 'os', 'adsid', 'picid', u'位置',  'pv', 'uv']
        c = 0
        for data in cl_name:
            worksheet.write(0, c, data)
            c += 1
        row_list = ['media_id', 'op', 'os', 'adsid', 'picid', 'area',  'pv', 'uv']
        r = 1

        for pic_name in self.picid_value:
            cl = 0
            for data_name in row_list:
                worksheet.write(r, cl, self.picid_value[pic_name][data_name])
                cl += 1
            r += 1
        workbook.save(excel_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('log statistic')
    parser.add_argument('-f', '--file', default=None, help='filename')
    args = parser.parse_args()
    log_value = an_log(args.file)
    if log_value:
        log_value.read_log()
        log_value.print_for()
        file_name1 = 'example2.xls'
        file_name = '/home/zjw/excel/toolbar_' + str(datetime.date.today() - datetime.timedelta(days=1))[2:] + '.xls'
        log_value.write_excel(file_name1)
