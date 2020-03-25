# coding:utf-8
import requests
import re
import time
import os


class Fund(object):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
        }
        # 15点前url
        self.url = 'http://fundgz.1234567.com.cn/js/{code}.js'
        # 获取估算的基金图片地址
        self.img_url = 'http://j4.dfcfw.com/charts/pic6/{code}.png'

        # 获取当天结算 http://8.jrj.com.cn/nss/ajaxFundInfo.jspa?fundcode=001071
        self.url_finally = "http://8.jrj.com.cn/nss/ajaxFundInfo.jspa?fundcode={code}"
        # nav 今天最新净值，
        # growthrate 今天最新涨跌幅，
        # totalnav 昨天净值，
        # monthrate1 近1月涨跌幅，
        # quartzrate1 近3月涨跌幅，
        # halfyearrate 近6月涨跌幅，
        # yearrate1 近1年涨跌幅，
        # threeyearrate 近3年涨跌幅，
        # baseyearrate 成立以来涨跌幅，

    def get_response(self, data):
        """
        请求15点前url，获取基金估算信息
        :return:
        """
        result = []
        # print(data)
        for code in data:
            response = requests.get(self.url.format(code=code['code']), headers=self.headers)
            responses = re.findall(r"\({(.+?)}\)", response.text)[0]
            data = responses.split(',')
            fund = {}
            # 基金信息
            for value in data:
                res = value.split(':')
                fund[res[0].strip("\"")] = res[1].strip("\"")
            fund['img_url'] = self.img_url.format(code=code['code'])
            result.append(fund)
        return result

    def get_content(self, data):
        """
        15点前拼接要发送的邮件信息
        :param data:
        :return:
        """
        time_stamp = self.show_time("%Y-%m-%d %H:%M")
        result = []
        for value in data:
            final_datas = {}
            content = ''
            content += '时间： ' + time_stamp + "\r\n"
            content += '#【' + value['name'] + '】(' + value['fundcode'] \
                       + ") \r\n 昨收： " + value['dwjz'] \
                       + '，今估算值： ' + value['gsz'] + "，\r\n估算涨跌幅： " \
                       + str(float(value['gszzl'])) + '%' + "\r\n"
            final_datas['content'] = content
            # 基金图片
            final_datas['file_path'] = self.make_img(value['img_url'], value['name'])
            result.append(final_datas)
        return result

    def get_finally_response(self, data):
        """
        请求22点最新url,获取基金当天更新后的最新信息
        :return:
        """
        result = []
        codes = []
        for code in data:
            codes.append(code['code'])
        self.url_finally = self.url_finally.format(code=",".join(codes))
        print(self.url_finally)
        response = requests.get(self.url_finally, headers=self.headers)
        response = response.json()
        if response['retcode'] == 0:
            res_data = response['list']

            for val in res_data:
                # for code in data:
                #     if val['fundcode'] == code['code']:
                        fund_data = {}
                        fund_data['fundcode'] = val['fundcode']  # code 基金代码，
                        fund_data['fundname'] = val['fundname']  # name 基金名称，
                        fund_data['nav'] = val['nav']  # nav 今天最新净值，
                        fund_data['growthrate'] = val['growthrate']  # growthrate 今天最新涨跌幅，
                        fund_data['totalnav'] = val['totalnav']  # totalnav 昨天净值，
                        fund_data['monthrate1'] = val['monthrate1']  # monthrate1 近1月涨跌幅，
                        fund_data['quartzrate1'] = val['quartzrate1']  # quartzrate1 近3月涨跌幅，
                        fund_data['halfyearrate'] = val['halfyearrate']  # halfyearrate 近6月涨跌幅，
                        fund_data['yearrate1'] = val['yearrate1']  # yearrate1 近1年涨跌幅，
                        fund_data['threeyearrate'] = val['threeyearrate']  # threeyearrate 近3年涨跌幅，
                        fund_data['baseyearrate'] = val['baseyearrate']  # baseyearrate 成立以来涨跌幅，
                        fund_data['d_value'] = [(val['nav'] - val['totalnav']) * code['number'] for code in data if
                                                val['fundcode'] == code['code']]  # 预估当天盈亏值，
                        result.append(fund_data)
                        # 　省时
                        # del data[data.index(code)]
        return result

    def get_finally_content(self, data):
        """
        晚上22点前拼接要发送的邮件信息
        :param data:
        :return:
        """
        time_stamp = self.show_time("%Y-%m-%d %H:%M")
        result = []
        print(data)
        for value in data:
            final_datas = {}
            content = ''
            content += '时间： ' + time_stamp + "\r\n"
            content += '# 【' + value['fundname'] + '】（' + value['fundcode'] + "）\r\n" \
                       + '涨跌幅： ' + str(value['growthrate']) + '%，' \
                       + '涨跌值： ' + str(round((value['nav'] - value['totalnav']), 4)) + "，\r\n" \
                       + '今天更新： ' + str(value['nav']) + '，' \
                       + '更新前: ' + str(value['totalnav']) + '，' + "\r\n" \
                       + '近1月涨跌幅： ' + str(round(value['monthrate1'], 2)) + '%，' \
                       + '近3月涨跌幅： ' + str(round(value['quartzrate1'], 2)) + '%，' + "\r\n" \
                       + '近6月涨跌幅： ' + str(round(value['halfyearrate'], 2)) + '%，' \
                       + '近1年涨跌幅： ' + str(round(value['yearrate1'], 2)) + '%，' + "\r\n" \
                       + '近3年涨跌幅： ' + str(round(value['threeyearrate'], 2)) + '%，' \
                       + '成立来涨跌幅： ' + str(round(value['baseyearrate'], 2)) + '%，' + "\r\n" \
                       + '收益估算为： ' + str(round(value['d_value'][0], 4)) + "\r\n\r\n"
            final_datas['content'] = content
            # 基金图片
            result.append(final_datas)
        return result

    def make_img(self, img_url, img_name):
        time_stamp = self.show_time("%Y%m%d")
        img_response = requests.get(img_url, headers=self.headers)
        # 获取当前目录绝对路径
        dir_path = os.path.dirname(os.path.abspath(__file__))
        file_path = dir_path + '/img/' + time_stamp
        if not self.make_dir(file_path):
            return False
        # file_path = './img/' + time_stamp + '/' + img_name + '.png'
        file_path = file_path + '/' + img_name + '.png'
        with open(file_path, 'wb') as f:
            f.write(img_response.content)
        return file_path

    @staticmethod
    def make_dir(file_path):
        file_path = file_path.strip()
        # print(file_path)
        is_exists = os.path.exists(file_path)
        if not is_exists:
            os.makedirs(file_path)
            # os.system('sudo mkdir ' + '\''+file_path+'\'')
        return True

    @staticmethod
    def show_time(style):
        return time.strftime(style, time.localtime())


def main():
    data = [
        '001071',  # 华安媒体互联网混合
        '006879',  # 华安智能生活混合
        '005962',  # 宝盈人工智能主题股票A
        '007874',  # 华宝科技ETF联接C
        '001028',  # 华安物联网主题股票
        '003096',  # 中欧医疗健康混合C
        '006113',  # 汇添富创新医药主题混合
    ]
    fund = Fund()
    funds_data = fund.get_finally_response(data)
    print(funds_data)
    send_content = fund.get_finally_content(funds_data)
    # print(send_content)


if __name__ == '__main__':
    main()
