def flatten_list(nested_list):
        """
        Recursively flattens nested lists.

        Example:
            flatten_list(['a', ['b', 'c'], [['d']]]) -> ['a', 'b', 'c', 'd']
        """
        flat_list = []
        for item in nested_list:
            if isinstance(item, list):
                flat_list.extend(flatten_list(item))
            else:
                flat_list.append(item)
        return flat_list