import requests
import re
from youxiang import YouXiang
from fund import Fund
from datetime import datetime


# 获取上证指数图片地址http://webquotepic.eastmoney.com/GetPic.aspx?nid=0.39906&imageType=r
class Shares(Fund):
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
        }
        super().__init__()

    def get_responses(self, resp_data):
        """爬取大盘信息"""
        result_datas = []
        for share_data in resp_data:
            url = 'http://api.money.126.net/data/feed/'
            exchange = "1" if (int(share_data['code']) // 100000 == 3) else "0"
            url += exchange + share_data['code'] + ","
            url = url[:-1]
            # print(url)
            responses = requests.get(url, headers=self.headers)
            responses = str(responses.content, 'utf-8')
            responses = re.findall(r":{(.+?)} }\)", responses)
            responses = responses[0]
            result = responses.split(', ')
            data = {}
            for value in result:
                res = value.split(': ')
                data[res[0].strip("\"")] = res[1].strip("\"").encode(encoding='utf-8').decode('unicode_escape')
            data['code'] = share_data['code']
            data['img_url'] = share_data['img_url']
            result_datas.append(data)
        return result_datas

    def sent_datas(self, result_datas):
        time_stamp = self.show_time("%Y-%m-%d %H:%M")
        # print(time_stamp)
        result = []
        for value in result_datas:
            final_datas = {}
            content = ''
            content += '时间： ' + time_stamp + "\n"
            content += '#【' + value['name'] + '】(' + value['code'] \
                       + ") \r\n" + '昨收： ' + str(round(float(value['yestclose']), 2)) \
                       + '，今开： ' + str(round(float(value['open']), 2)) + "，\r\n" \
                       + '最高： ' + str(round(float(value['high']), 2)) + '，最低： ' + str(round(float(value['low']), 2)) \
                       + '， 现在： ' + str(round(float(value['price']), 2)) + "，\r\n" \
                       + '涨跌额： ' + str(round(float(value['updown']), 2)) + '，涨跌幅： ' \
                       + str(round(float(value['percent']) * 100, 2)) + '%' + "\r\n\r\n"
            # print(value['img_url'])
            final_datas['content'] = content
            final_datas['file_path'] = self.make_img(value['img_url'], value['name'])
            result.append(final_datas)
        return result


def main():
    share_data = [
        {"code": "000001",
         "img_url": "http://webquotepic.eastmoney.com/GetPic.aspx?nid=1.000001&imageType=r"},  # sh000001 上证指数
        {"code": "399006",
         "img_url": "http://webquotepic.eastmoney.com/GetPic.aspx?nid=0.399006&imageType=r"}  # sz399006 创业板指
    ]
    # fund_data = [
    #     {"code": "001071",
    #      "img_url": "http://j4.dfcfw.com/charts/pic6/001071.png"},  # 华安媒体互联网混合
    #     {"code": "006879",
    #      "img_url": "http://j4.dfcfw.com/charts/pic6/006879.png"},  # 华安智能生活混合
    #     {"code": "005962",
    #      "img_url": "http://j4.dfcfw.com/charts/pic6/005962.png"},  # 宝盈人工智能主题股票A
    #     {"code": "007874",
    #      "img_url": "http://j4.dfcfw.com/charts/pic6/007874.png"},  # 华宝科技ETF联接C
    #     {"code": "001028",
    #      "img_url": "http://j4.dfcfw.com/charts/pic6/001028.png"},  # 华安物联网主题股票
    #     {"code": "003096",
    #      "img_url": "http://j4.dfcfw.com/charts/pic6/003096.png"},  # 中欧医疗健康混合C
    #     {"code": "006113",
    #      "img_url": "http://j4.dfcfw.com/charts/pic6/006113.png"},   # 汇添富创新医药主题混合
    # ]
    fund_data = [
        {"code": "001071", "number": 2642.37},  # 华安媒体互联网混合
        {"code": "006879", "number": 3277.28},  # 华安智能生活混合
        {"code": "005963", "number": 1921.22},  # 宝盈人工智能主题股票C
        {"code": "007874", "number": 3016.99},  # 华宝科技ETF联接C
        {"code": "008084", "number": 4350.52},  # 海富通先进制造股票C
        {"code": "519674", "number": 550.00},  # 银河创新成长混合
    ]
    # 大盘信息
    share = Shares()
    response_data = share.get_responses(share_data)
    print(response_data)
    send_share_datas = share.sent_datas(response_data)
    smtp = YouXiang('smtp.qq.com', 465, '395053387@qq.com', 'ebwalwpgdwbzbiba', '395053387@qq.com', 'valorayan@126.com',
                    '股盘及基金信息')
    # 邮箱中填充发送的上证指数，创业扳指信息
    for send_share_data in send_share_datas:
        smtp.add_content(send_share_data['content'])
        smtp.add_img(file_path=send_share_data['file_path'])
    # 基金信息
    fund = Fund()
    # 现在时间
    now_time = datetime.now()
    # night_time = datetime.strptime(str(datetime.now().date()) + '22:00', '%Y-%m-%d%H:%M')
    night_time = datetime.strptime(str(datetime.now().date()) + '11:00', '%Y-%m-%d%H:%M')
    if now_time >= night_time:
        # 最终结果
        funds_data = fund.get_finally_response(fund_data)
        send_fund_datas = fund.get_finally_content(funds_data)
        print(send_fund_datas)
        for send_fund_data in send_fund_datas:
            smtp.add_content(send_fund_data['content'])
    else:
        funds_data = fund.get_response(fund_data)
        send_fund_datas = fund.get_content(funds_data)
        print(send_fund_datas)
        for send_fund_data in send_fund_datas:
            smtp.add_content(send_fund_data['content'])
            smtp.add_img(file_path=send_fund_data['file_path'])
    smtp.send_email()
    smtp.close_email()
    print("发送成功")


if __name__ == "__main__":
    main()
