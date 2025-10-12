line = 'OK+0000OK+ANCSWOK+ANCS:14com.apple.moOK+ANCS:09bilephone'

event_id = line[3:7]
print(event_id)

print(line.split('OK+'))