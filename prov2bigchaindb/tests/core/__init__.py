import pkg_resources


def setup_test_files():
    test_resources = {
        'simple': {'package': 'prov2bigchaindb', 'file': '/assets/graph-example.json'},
        'simple2': {'package': 'prov2bigchaindb', 'file': '/assets/test-example.json'},
        'quantified': {'package': 'prov2bigchaindb', 'file': '/assets/quantified-self.json'},
        'thesis': {'package': 'prov2bigchaindb', 'file': '/assets/thesis-example-full.json'}
    }
    return dict(
        (key, pkg_resources.resource_string(val['package'], val['file'])) for key, val in test_resources.items()
    )
