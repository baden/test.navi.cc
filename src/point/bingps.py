# -*- coding: utf-8 -*-
import httplib
import urllib
import urllib2
from struct import pack, unpack
from httplib import HTTP

from datetime import datetime, timedelta
import struct
from random import randint

#GETFROM = "gps-maps.appspot.com:80"
from config import *

'''
struct.unpack(fmt, string)
struct.unpack_from(fmt, buffer[, offset=0])
'''

PACK_F2 = '<BBBBBBBBBBBBBBBBBBBBBBHHBBHBB'
#          ^ - D0: Заголовок (должен быть == 0xFF)
#           ^ - D1: Идентификатор пакета (должен быть == 0xF2)
#            ^ - D2: Длина пакета в байтах, включая HEADER, ID и LENGTH (32)
#             ^ - D3	день	День месяца = 1..31
#              ^ D4	месяц | ((год-2010) << 4)	Месяц = 1..12 год = 0..14 → 2010..2024
#               ^ D5	Часы	Часы = 0..23
#                ^ D6	Минуты	Минуты = 0..59
#                 ^ D7	Cекунды	Cекунды = 0..59
#                  ^ D8	Широта (LL)	Градусы широты = 0..89
#                   ^ D9	Широта (ll)	Минуты целая часть = 0..59
#                    ^ D10	Широта (mm)	Минуты дробная часть1 = 0..99
#                     ^ D11	Широта (nn)	Минуты дробная часть2 = 0..99
#                      ^ D12	Долгота (LLL)	Градусы долготы = 0..179
#                       ^ D13	Долгота (ll)	Минуты целая часть = 0..59
#                        ^ D14	Долгота (mm)	Минуты дробная часть1 = 0..99
#                         ^ D15	Долгота (nn)	Минуты дробная часть2 = 0..99
#                          ^ D16	D16.0 = NS	D16.1 = EW	D16.2 = (Course & 1)	D16.0=0 для N	D16.0=1 для S	D16.1=0 для E	D16.1=1 для W	D16.2=0 для четных Course	D16.2=1 для нечетных Course
#                           ^ D17	Спутники	Кол-во спутников 3..12
#                            ^ D18	Скорость	Скорость в узлах 0..239
#                             ^ D19	Скорость дробная часть	Дробная часть скорости 0..99
#                              ^ D20	Направление	Направление/2 = 0..179
#                               ^ D21	Направление дробная часть	Дробная часть направления 0..99
#                                ^ D22, D23	Напряжение внешнего питания	Напряжение/100 = 0..2000	D22 – младшая часть	D23 – старшая часть
#                                  ^ D24, D25	Напряжение внутреннего аккумулятора	Напряжение/100 = 0..5000	D24 – младшая часть	D25 – старшая часть
#                                    ^ D26	Зарезервировано	=0
#                                     ^ D27	Тип точки	Причина фиксации точки
#                                      ^ D28, D29	Неточное смещение	Смещение относительно точного времени в секундах. Значение 0xFFFF означает превышение лимита и должно игнорироваться если это возможно.
#                                        ^ D30	Зарезервировано	=0
#                                         ^ D31	Зарезервировано	=0

assert(struct.calcsize(PACK_F2) == 32)

g_time = datetime.utcnow()

CRC16_CCITT_table = (
        0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7, 0x8108, 0x9129, 0xa14a, 0xb16b,
        0xc18c, 0xd1ad, 0xe1ce, 0xf1ef, 0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
        0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de, 0x2462, 0x3443, 0x0420, 0x1401,
        0x64e6, 0x74c7, 0x44a4, 0x5485, 0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
        0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6, 0x5695, 0x46b4, 0xb75b, 0xa77a, 0x9719, 0x8738,
        0xf7df, 0xe7fe, 0xd79d, 0xc7bc, 0x48c4, 0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823,
        0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b, 0x5af5, 0x4ad4, 0x7ab7, 0x6a96,
        0x1a71, 0x0a50, 0x3a33, 0x2a12, 0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
        0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41, 0xedae, 0xfd8f, 0xcdec, 0xddcd,
        0xad2a, 0xbd0b, 0x8d68, 0x9d49, 0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,
        0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78, 0x9188, 0x81a9, 0xb1ca, 0xa1eb,
        0xd10c, 0xc12d, 0xf14e, 0xe16f, 0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
        0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e, 0x02b1, 0x1290, 0x22f3, 0x32d2,
        0x4235, 0x5214, 0x6277, 0x7256, 0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
        0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405, 0xa7db, 0xb7fa, 0x8799, 0x97b8,
        0xe75f, 0xf77e, 0xc71d, 0xd73c, 0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
        0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab, 0x5844, 0x4865, 0x7806, 0x6827,
        0x18c0, 0x08e1, 0x3882, 0x28a3, 0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
        0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0, 0x2ab3, 0x3a92, 0xfd2e, 0xed0f, 0xdd6c, 0xcd4d,
        0xbdaa, 0xad8b, 0x9de8, 0x8dc9, 0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,
        0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8, 0x6e17, 0x7e36, 0x4e55, 0x5e74,
        0x2e93, 0x3eb2, 0x0ed1, 0x1ef0
        )

def CRC16(crc, data):
    """ Compute correct enough :grin: CRC16 CCITT for using in BF2142 auth token """
    return (((crc << 8) & 0xff00) ^ CRC16_CCITT_table[((crc >> 8) ^ (0xff & data))])

g_lat = 48.370848
g_lon = 32.717285

def add_point(dt):
	global g_lat, g_lon, g_time
	time = g_time + timedelta(seconds=dt)
	lat = g_lat
	lon = g_lon

	lat_s = 0
	if lat < 0:
		lat_s = 1
		lat = -lat
		
	lat_i = int(lat)
	lat_f = (lat - lat_i) * 60.0
	lat_t = int((lat_f - int(lat_f)) * 10000)

	lon_s = 0
	if lon < 0:
		lon_s = 2
		lon = -lon
		
	lon_i = int(lon)
	lon_f = (lon - lon_i) * 60.0
	lon_t = int((lon_f - int(lon_f)) * 10000)

	packet = struct.pack(PACK_F2,
		0xFF,		# D0: Заголовок (должен быть == 0xFF)
		0xF2,		# D1: Идентификатор пакета (должен быть == 0xF2)
		32,		# D2: Длина пакета в байтах, включая HEADER, ID и LENGTH (32)
		time.day,	# D3	день	День месяца = 1..31
		time.month + (time.year-2010)*16,		# D4	месяц | ((год-2010) << 4)	Месяц = 1..12 год = 0..14 → 2010..2024
		time.hour,	# D5	Часы	Часы = 0..23
		time.minute,	# D6	Минуты	Минуты = 0..59
		time.second,	# D7	Cекунды	Cекунды = 0..59
		lat_i,		# D8	Широта (LL)	Градусы широты = 0..89
		int(lat_f),	# D9	Широта (ll)	Минуты целая часть = 0..59
		lat_t // 100,	# D10	Широта (mm)	Минуты дробная часть1 = 0..99
		lat_t % 100,	# D11	Широта (nn)	Минуты дробная часть2 = 0..99
		lon_i,		# D12	Долгота (LLL)	Градусы долготы = 0..179
		int(lon_f),	# D13	Долгота (ll)	Минуты целая часть = 0..59
		lon_t // 100,	# D14	Долгота (mm)	Минуты дробная часть1 = 0..99
		lon_t % 100,	# D15	Долгота (nn)	Минуты дробная часть2 = 0..99
		lat_s + lon_s,	# D16	D16.0 = NS	D16.1 = EW	D16.2 = (Course & 1)	D16.0=0 для N	D16.0=1 для S	D16.1=0 для E	D16.1=1 для W	D16.2=0 для четных Course	D16.2=1 для нечетных Course
		randint(3,12),	# D17	Спутники	Кол-во спутников 3..12
		randint(9,100),	# D18	Скорость	Скорость в узлах 0..239
		randint(0,99),	# D19	Скорость дробная часть	Дробная часть скорости 0..99
		randint(0,179),	# D20	Направление	Направление/2 = 0..179
		randint(0,99),	# D21	Направление дробная часть	Дробная часть направления 0..99
		randint(0,2000),# D22, D23	Напряжение внешнего питания	Напряжение/100 = 0..2000	D22 – младшая часть	D23 – старшая часть
		randint(0,5000),# D24, D25	Напряжение внутреннего аккумулятора	Напряжение/100 = 0..5000	D24 – младшая часть	D25 – старшая часть
		randint(0,255),	# D26	Зарезервировано	=0
		13,		# D27	Тип точки	Причина фиксации точки
		0,		# D28, D29	Неточное смещение	Смещение относительно точного времени в секундах. Значение 0xFFFF означает превышение лимита и должно игнорироваться если это возможно.
		randint(0,255),	# D30	Зарезервировано	=0
		randint(0,255)	# D31	Зарезервировано	=0
	)
	return packet

def main():
	global g_lat, g_lon, g_time

	with open('.saveit.tmp', 'rb') as f:
		g_lat, g_lon = struct.unpack('ff', f.read(8))
	print 'g_lat, g_lon=', g_lat, g_lon

	body=''
	#for i in xrange(6000):
	for i in xrange(256):
		body += chr(i)

	for i in xrange(15):
		body += add_point(i)
		g_lat += 0.00005
		g_lon += 0.00005

	_log = '\n==\t\tEncoded data (HEX):'
	crc = 0
	for byte in body:
		crc = CRC16(crc, ord(byte))
		_log += ' %02X' % ord(byte)

	print _log

	print 'CRC: %04X' % crc

	body += struct.pack('<H', crc)

	rawPOST2('/bingps?imei=%s' % (IMEI), body)

	with open('.saveit.tmp', 'wb') as f:
		f.write(struct.pack('ff', g_lat, g_lon))

if __name__ == "__main__":
	main()
