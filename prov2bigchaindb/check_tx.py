from bigchaindb_driver import BigchainDB
from prov.model import ProvDocument


b = BigchainDB('http://127.0.0.1:9984')
id = '2951ce66e93f146601f6b4cdce155115d80124ba0ec0d2b7234c3ab5659e07e6'

def get_asset(id):
    return b.transactions.get(asset_id=id)[0]

tx = b.transactions.get(asset_id=id)[0]
print(tx)
print()

if tx['asset'].get('id'):
    tx = get_asset(tx['asset']['id'])
    print(tx)
    print()

doc = ProvDocument.deserialize(content=tx['asset']['data'].get('prov'), format='json')
print()
print(doc.get_provn())
print()
map = tx['asset']['data'].get('map')

print(map)
print('===========')

for id in map.values():
    tx = get_asset(id)
    print(tx)
    print()
    if tx['asset'].get('id'):
        tx = get_asset(tx['asset']['id'])
        print(tx)
        print()

