from prov.model import ProvDocument
import rethinkdb as r
r.connect("localhost", 28015, db='bigchain').repl()
#res = r.table('bigchain').get_field("block").get_field("transactions").run()
res = r.table('bigchain').get_field("block").pluck({'transactions': ['id','operation','asset']}).run()
tx_ids = []

for d in res:
    for dd in d['transactions']:
        if dd['operation'] == 'CREATE':
            #print(dd)
            tx_ids.append([dd['id'],dd['asset']])
print(tx_ids)

from bigchaindb_driver import BigchainDB
b = BigchainDB('http://127.0.0.1:9984')
tx = b.transactions.retrieve(tx_ids[0][0])
doc = ProvDocument.deserialize(content=tx['asset']['data']['prov'], format='json')
print(doc.get_provn())

print(tx_ids[0][0])
res = r.table('bigchain').get_field("block").pluck({'transactions': ['id','asset']}).filter({"transactions"}).run()
print(res)
#res = r.table('bigchain').get_field("block").pluck({'transactions': ['id','asset']}).replace('asset':'s').run()
    #
    #
    # .update(lambda tx:
    # r.branch(
    #     tx["id"] == tx_ids[0][0],
    #     {"asset": {"data":{"prov":{"{}"}}}},
    # )).run()
#print(res)