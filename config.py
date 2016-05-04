from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
parser.read('pyshake.conf')

db_path = parser.get('General', 'db_path')
pyrit_path = parser.get('General', 'pyrit_path')
cap_path = parser.get('General', 'cap_path')