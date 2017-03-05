from bigchaindb_driver import BigchainDB
from prov.model import ProvDocument
from prov2bigchaindb.core import utils


def main():
    b = BigchainDB('http://127.0.0.1:9984')
    count = 0
    def get_asset(tx_id):
        return b.transactions.get(asset_id=tx_id)[0]

    tx_ids = ['c59250e003afecbe52443fb4a1683954b28d897f6c8a68c796af7e3efb2bf6b3', 'bd330babcedebc68a857e783b4d06596cd347d9179f18685b5c97480df4ac814', '01c4d950f97a3691cebf7e7cd37d8ecbeaa55ea5ce0d96b6a6806a1db908330c', 'bf92f5441c895f8a2f1209816bdacee8d6d5b7e2e9b1b266e9690b56c5a4e10c', '03f470095fb7aece7bb3088a401044db5c05c22a3dfa1942749b58a488be51c6', '3e6404b838ff93ff61d5b3736a57418e950a4c939fad03852ea1c15b3cc2c84b', '67b1defc3f427c810fbfd81257c023f3ab0d97c518dc65e68da8647ccf814b63', '336246d841f4c3d7f87f11d000bc7116c2e1c042cbd11f85a101d610490692aa', '2a4f543a966a49bf6e4d1e89f050d5631d5d5250a42db0dd2e95d9a76510ad3e', '51c904c1afc03d0fc9c7f299768f590ad5c49df92c3fb7de1b0dc62a63b72f06', '26d3bce0063e3e70c0d5b9ce32fdc4b587cf6ca2889e9387fb7a5fb3fd39fbb5', 'f8c6c614016dc6df11cf0641b34f58016b72aaac4b696344f95e04fb7f08d592', '3e63ea75c944518c96f203f83c348ec217b1b437c3968e30cbb7e28762038c3d', 'f4bcda946b8db27d8124b960f330974960e23c24c78d8007306a4831f875053b', 'eb02019cab77ab00245505c0f9b395f0f916fbd5c7d61c3f1fce2c01befa3666', '1d0c7e7cef6b981f66efbe2458f22aca450ee91539b301a47f9be8eb729b94dd', 'ee7cb82a8ae320694bb7e8f0c9e009b210f64c8362915133e0388b97d2434ea9', '84776013633b2736e6dc9a17309b200563235e0bc494bceb54edb623f8055e00', '50f6557e3f44add436e78613a44a945217f09c88945f08183ed27f7491f97e8d']

    for tx_id_in in tx_ids:
        # tx_id_in = '2951ce66e93f146601f6b4cdce155115d80124ba0ec0d2b7234c3ab5659e07e6'

        tx = b.transactions.get(asset_id=tx_id_in)[0]
        #print(tx)
        #print()

        if tx['asset'].get('id'):
            tx = get_asset(tx['asset']['id'])
            #print(tx)
            #print()

        doc = utils.to_prov_document(tx['asset']['data'].get('prov'))
        print()
        print(doc.get_provn())
        print()
        count += 1
        mapping = tx['asset']['data'].get('map')

        print(mapping)
        print('===========')

        #if mapping:
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
