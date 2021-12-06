# coding:utf-8
import hmac

def test_1():
    secret_key1 = b'This is my secret key'
    message1 = b'Hello world'
    hex_res1 = hmac.new(secret_key1, message1, digestmod="MD5").hexdigest()
    print("*" * 100)
    print(hex_res1)

    content = "hello world"
    content_bytes = content.encode("utf-8")
    content_bytes_upper = content_bytes.upper()  # 今天才知道,还可以对bytes进行upper
    print(content_bytes_upper.decode("utf-8"))  # HELLO WORLD