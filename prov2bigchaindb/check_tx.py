from bigchaindb_driver import BigchainDB
from prov.model import ProvDocument
from prov2bigchaindb.core import utils


def main():
    b = BigchainDB('http://127.0.0.1:9984')

    def get_asset(tx_id):
        return b.transactions.get(asset_id=tx_id)[0]

    tx_id_in = '2951ce66e93f146601f6b4cdce155115d80124ba0ec0d2b7234c3ab5659e07e6'

    tx = b.transactions.get(asset_id=tx_id_in)[0]
    print(tx)
    print()

    if tx['asset'].get('id'):
        tx = get_asset(tx['asset']['id'])
        print(tx)
        print()

    doc = utils.to_prov_document(tx['asset']['data'].get('prov'))
    print()
    print(doc.get_provn())
    print()
    mapping = tx['asset']['data'].get('map')

    print(mapping)
    print('===========')

    for tx_id in mapping.values():
        tx = get_asset(tx_id)
        print(tx)
        print()
        if tx['asset'].get('id'):
            tx = get_asset(tx['asset']['id'])
            print(tx)
            print()


if __name__ == "__main__":
    main()
