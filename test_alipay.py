import urllib

from alipay import AliPay
import qrcode, time

DEBUG=True
APPID = '2016102100732845'
APP_PRIVATE_KEY = '''-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAqSlXzwpHVcCtVV5OB5JLUWEwgnJMXNY4POd5tTACt4RUocm91YxIjlN5uLe04RlYfaWPM0XrwDaVmA5UaTrngtX4e/TDBXlFXJCs3JH7Xc5r8KhqUwmR1Fc0BoBtyTaB+rwhYHcPD07xmZ0h4K8UzAlki70jEhZmQxtf1JQCvdWOkJie7+ojuPB6DE/054wPkyD0imK9LOWQWRjeT2fzLMkAxXNixfNFoyvjos37DJ2ojSyyzDU5B5n2qrdyCzfZbMBzXgg/sqEvKKqz4p8n70Im9Ly2DQbQ8ytpPcn6QER0K4zBNab7nxaHZQe1/YVDWhmVtafnaUpftKgemFszqQIDAQABAoIBAGk1RV+HTQaQZz2JAY7D9gQPJlR7MfMraJ64eIGv8oCg1OIqzt5Z+WZLlJDF8MFvOhIrPfztp8pMKI4Bm443DHXbDkhJ2mE1I2aGtHwabvPQxmFO3ZH3ibM+6SSCC8XxGLYQ+9E7OyqSNsELcV6EhbLAxMAESiOdusxR4jAcPfhCLJMg97RXIX+YQGoDpj2E3427DPXWX+65msvQJL6vjhK5wTAwxLeQi7S08A59uV3xJ9mWuqc5mwxiXe9oE/GIBGc9M859kPZdZvnwuH9lqX3JgWUTQZExKSYafDm4gMfhkqn//HC2Eo4gdVXb2Cavar9taUrmdBTQX2Uv3e69NuECgYEA75dYjflknFDcxs+zaIXGWO6HvtNPRGV8z9PYnSZ7NIpMLxiVM2uUqgfXI56byqbBjpCN5qiTPFp4T5svkvPwj1ouZP/lu3I/rdGhs5FYFoHi1fAQFC0uOfS8JGCFw7leN5wXHFjjPKojcdV9OqU8oZU35X6qbxw1SzZHg4QJLhMCgYEAtL8unQN+AXXiKH7CVM2hJzn2JZSv8yUBsHVOBKv85M6NxwLTTRidmE7NqSIbIJkLPtmB+u4x+dMu8/mi4eUCHU8BblAocvFBNtSMx4od3H9KhSGv20bh0fyNgIeEqXxiICY6qm9qPQvXrcOwLaZRQ94nbKIDqBBbpfggX2WMHtMCgYAWclt9kav3aSwGBFeOp1nZ4x8cpbd7dPaokfRtZLmORpa0otz3oFChTXK+h5GY/t6LeMeSoKCKuv8ility3R/gjlZiaAch9KY6prU7mZZjJXAXExKukT0PePpXfiOKHsfQ9fLEWR+RA2+mrpW49NolWVGPUrqtBjuH/GHe1HP3uQKBgHUkr2ZN/B2gNFqAhRyHRRnyQ+jpa/vPEUA3VsBKY5Y7lMHVv/LosEMlV791flVrO1GZkNd8B2HeEEFJmtqDHRK3wLqpMv4EBHsv2Kn+hwoAaeDNC3e3geYho+gYbM+X8NTbUgxiN12nTjqtaIK9l0/ALJcIjgwfxfZUUU7itqTHAoGAY5GfRM49SjuyM4M65Lwz2XrulgxodZLdI+dKDUPMqpXwgBeP14ci8Mm5ldub13RKanDxtF92byAoI/Yn6xe8zynVgIFmIKI6yf7rk5NA8fGbDeRoLxnSJnMNxihNbS/n799YpXTa5dywl8lCw8kaxdZ+6hz+EZH/wAF24zAfPzo=
-----END RSA PRIVATE KEY-----
'''
ALIPAY_PUBLIC_KEY = '''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwy7Xzzm9XnT3Clb2wGmO5O/N1/jpiEgIVomCYiFJJCvADlMdPuVcFaRPYMDj2cE6f2w+MiJQucTazpAbOxC0PQMwcjfFjENVvk0ZfuJwWLQI0bOdbiCN79iaPstjqHgrSFKbU3njuoFkbKImKCu4YbgiQoq+vXan+M80QLhVafMmIqa0jDOBLpqF3iw1xsl0FHxfkRFodHs1obF0cj6Z2qbpzele+LGlkTI9J2l0NIXPDaA0S/w1nsLqN5yfMzExpDxcY+PlQCwSgHPzVqwkQ4dspbEKy+RxJTIbuTJpPNbiVvZwsc3WmxrWzvFH9jk2mr7LccjNbxPVOwOIoJLMCwIDAQAB
-----END PUBLIC KEY-----
'''

alipayClient = AliPay(
    appid=APPID,
    app_notify_url=None,
    app_private_key_string=APP_PRIVATE_KEY,
    alipay_public_key_string=ALIPAY_PUBLIC_KEY,
    sign_type='RSA2',
    debug=DEBUG,
)


# 生成二维码图片
def get_qr_code(code_url):
    """
    生成二维码
    :return None
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=1
    )
    qr.add_data(code_url)  # 从URL获取二维码所含信息
    img = qr.make_image()  # 生成二维码图片
    img.save(r'qr_test_ali.png')
    print('二维码保存成功！')


# 查询订单支付状态
def query_order(out_trade_no: int):
    """
    :param out_trade_no: 商户订单号
    :return: result: 支付结果
    """
    _time = 0
    for i in range(600):
        time.sleep(1)
        result = alipayClient.api_alipay_trade_query(out_trade_no=out_trade_no)
        print('订单查询返回值：', result)
        if result.get("trade_status", "") == "TRADE_SUCCESS":
            print('订单已支付!')
            print('订单查询返回值：', result)
            return True
        _time += 2
    return False


if __name__ == '__main__':
    out_trade_no = "562"  # 555 开始
    total_amount = 1.00
    subject = "relive"
    timeout_express = '1m'
    try:
        dict = alipayClient.api_alipay_trade_precreate(out_trade_no=out_trade_no, total_amount=total_amount,
                                  subject=subject, timeout_express=timeout_express)
    except urllib.error.URLError:
        print('网络已断开')
        exit()
    print(dict)
    print('test')
    get_qr_code(dict['qr_code'])
    query_order(out_trade_no)
