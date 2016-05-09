import app
d = app.capfileobj()
d.path = 'data/cap/wpa.cap'
d.name = 'wpa.cap'
print d.cap_get_essids()
e = app.essidobj()
e.name = 'test'
e.process()
