from bigchaindb_driver import BigchainDB

from prov2bigchaindb.core import utils


def main():
    b = BigchainDB("http://129.247.111.205:49984")
    count = 0

    def get_asset(tx_id):
        return b.transactions.get(asset_id=tx_id)[0]

    tx_ids = ['783744dd35db3120e6c92223634898744de9881665b89d19826de3a2f1393587', '09f58468d59bc79e6dfa0aa561a2b6c4a1b19e88ba648a6f5b00ab044f5233c9', '999a475ece5c97317dacd792b6f4e7eed9466093a80c4ff701fa9434bee123b0', 'fb81fb72c582e949e1854771757ead766f920dae7db54c9a8108f13af1cd1a57', '4634844549f036813a4486b1bedecd4f1c3a93faa2e3272e236514521a5ce1ec', '7ec3d1bd0996ea15958486e238136803c3e964e3b7ed82a3a15fa06921651301', '555ca9154436c2f667feb76b6cbe0ed51d00c5d34f572fe17d6222a7432c9f3c', '80acab7eb130bc452522487fdfba2967cc2d4b4633aecc8e00649b56fbf155c1', 'f7c6c59d43e31d90cec917e8db7b83fe1e77bb91cb88fe21dab85c08ab7cb165', 'b07ff802de79819216fa7cb7278a996d8648be71c9c74dcebe1610408aae5508', 'f00a7b16f5d22f0bdb35dc61dd04c5f786e70a93aefba47e3fe55397ceecc0d2', '734c6d46f3838dafdcaf66ebbd608817b8b2c39d51f438866aa919ee5999d4c5', '8aea5ea956e15f103207958ea51a76b0938a2da9d9a069af6214d8042f373356', 'e1325132cfbc5417773590100fc4dc546d32e91510973b512c2e57eb0aae71fd', '5a5a5d9575a110a18eeabf8c7b6e834d14b22991b8a854f15ca2220d921277b0', '63e8e47e96fbb418ca54e2f47c3f1445c1849e0079be366b0d0b3c0f6abb3f34', 'e19060c543baaea3f843a5d2038139fd6d16bb5aef5a1be7c5187d87d36e4881', 'bd849176c3b636cf51d7fad8ac368b64514ab61798a482dd2cc8423a329e10ce', '95c12de4e1597babcd481a560905e8fee83cd114c9d87a7d2bf175ae9388a238', '2cdc982f04e9a8175e9d1ec5ac97e78e1ede1da904e739513d14222f28875f37']


    for tx_id_in in tx_ids:
        # tx_id_in = '2951ce66e93f146601f6b4cdce155115d80124ba0ec0d2b7234c3ab5659e07e6'

        tx = b.transactions.get(asset_id=tx_id_in)[0]
        # print(tx)
        # print()

        if tx['asset'].get('id'):
            tx = get_asset(tx['asset']['id'])
            # print(tx)
            # print()

        doc = utils.to_prov_document(tx['asset']['data'].get('prov'))
        print()
        print(doc.get_provn())
        print()
        count += 1
        mapping = tx['asset']['data'].get('map')

        print(mapping)
        print('===========')

        # if mapping:
        #    for tx_id in mapping.values():
        #        tx = get_asset(tx_id)
        #        print(tx)
        #        print()
        #        if tx['asset'].get('id'):
        #            tx = get_asset(tx['asset']['id'])
        #            print(tx)
        #            print()
    print("count", count)
    print("init tx_ids", len(tx_ids))


if __name__ == "__main__":
    main()
