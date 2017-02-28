from prov.model import ProvDocument
from bigchaindb_driver import BigchainDB
b = BigchainDB('http://127.0.0.1:9984')
import rethinkdb as r
r.connect("localhost", 28015, db='bigchain').repl()
#res = r.table('bigchain').get_field("block").get_field("transactions").run()
#res = r.table('bigchain').get_field("block").pluck({'transactions': ['id','operation','asset','metadata']}).run()
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

tx = b.transactions.retrieve(tx_ids[0]['tx_id'])
print(tx,end='\n\n')
doc = ProvDocument.deserialize(content=tx['asset']['data']['prov'], format='json')
print(doc.get_provn())

#asset = {'data':{}}
#res = r.table("bigchain").get(tx_ids[0]['block_id']).run()
#print(res)
#.update(
#    {contact: {phone: {cell: "408-555-4242"}}}

#res = r.table("bigchain").get(tx_ids[0]['block_id']).get_field('block').get_field('transactions').get_field('asset').get_field('data').replace({'prov':{'news':'fake'}}).run()
#.update({'block':{'transactions':[{'asset':r.literal(asset)}]}}).run()
#print(res)

#res = r.table("bigchain").get(tx_ids[0]['block_id']).run()
#print(res)

#tx = b.transactions.retrieve(tx_ids[0]['tx_id'])
#print(tx,end='\n\n')
#doc = ProvDocument.deserialize(content=tx['asset']['data']['prov'], format='json')
#print(doc.get_provn())