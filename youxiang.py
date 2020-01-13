# coding:utf-8
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


class YouXiang(object):
    def __init__(self, host, port, mail_user, mail_password, From, To, title):
        # 链接到smtp服务器
        self.host = host
        self.port = port
        self.smtp = smtplib.SMTP_SSL(self.host, self.port)
        # 登录smtp服务器
        self.smtp.login(user=mail_user, password=mail_password)
        self.From = From
        self.To = To
        # 创建一封带附件的邮件
        self.msg = MIMEMultipart()
        # 主题
        self.msg['Subject'] = Header(title, charset='utf-8')
        # 发件人
        self.msg['From'] = self.From
        # 收件人
        self.msg['To'] = self.To
        self.img_num = 0

    def add_content(self, Content):
        # 创建邮件文件内容对象
        content = MIMEText(Content, _charset='utf-8')
        # 把邮件文本内容，添加到多组件的邮件中
        self.msg.attach(content)
        return self.msg

    def add_img(self, file_path):
        """图片"""
        with open(file_path, 'rb') as f:
            img_content = f.read()
        app = MIMEImage(img_content)
        app.add_header('Content-ID', '<image%d>' % self.img_num)
        self.img_num += 1
        self.msg.attach(app)

    def send_email(self):
        self.smtp.send_message(msg=self.msg, from_addr=self.From, to_addrs=self.To)

    def close_email(self):
        self.smtp.quit()


# mail_user = '395053387@qq.com'
# mail_password = 'ebwalwpgdwbzbiba'

if __name__ == "__main__":
    smtp = YouXiang('smtp.qq.com', 465, '395053387@qq.com', 'ebwalwpgdwbzbiba', '395053387@qq.com', 'valorayan@126.com',
                    '股盘及基金信息')
    smtp.add_content('封装发送内容')
    smtp.add_img(file_path='./创业板指.png')
    smtp.send_email()
