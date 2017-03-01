from prov.model import ProvDocument
from bigchaindb_driver import BigchainDB
b = BigchainDB('http://127.0.0.1:9984')

import rethinkdb as r
r.connect("localhost", 28015, db='bigchain').repl()

res = r.table('bigchain').pluck('id',{'block':{'transactions': ['id','operation','asset','metadata']}}).run()

tx_ids = []
for doc in res:
    block_id = doc['id']
    for tx in doc['block']['transactions']:
        if tx['operation'] == 'CREATE' and 'relation' in tx['metadata'].keys():
            #print(dd)
            tx_ids.append({'block_id':block_id,'tx_id':tx['id'],'doc':doc})

#print(tx_ids)
#print("GOT: ", len(tx_ids),end='\n\n')
#[print(entry,end='\n\n') for entry in tx_ids[0].values()]

#print(tx_ids[0]['doc']['block']['transactions'])
#tx = b.transactions.retrieve('2d6b70c4d64239fea7eeacde312bb451c0317f93f09a3272fdcc06562c5e60aa')
#doc = ProvDocument.deserialize(content=tx['asset']['data']['prov'], format='json')
#print(doc.get_provn())

#res = r.table("bigchain").get(tx_ids[0]['block_id']).run()

asset = {'data':{'prov':{}}}
block = r.table('bigchain').get_all(tx_ids[0]['tx_id'], index='transaction_id')['block']['transactions'].for_each(lambda tx: r.branch((tx['id'] == tx_ids[0]['tx_id']), tx.replace({'asset':asset}), tx)).run()
print(block, end='\n\n')
