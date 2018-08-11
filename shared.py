from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def ip_to_int(ip_str):
    # TODO: IPv6 support
    segments = [int(s) for s in ip_str.split(".")]
    segments.reverse()
    ip_num = 0
    for segment in segments:
        ip_num = ip_num | segment
        ip_num = ip_num << 8
    return ip_num
