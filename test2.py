from dateutil.parser import parse
a = parse('2017-10-01/12:12:12')
b = parse('2013-3-4/10:10:10')
print((a - b).days)
print((a - b).seconds)
print((a - b).total_seconds())