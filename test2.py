
from dateutil.parser import parse
a = parse('2021-11-22T09:59:19.000Z')
b = parse('2021-11-22T10:59:19.000Z')

print((b - a).seconds)
