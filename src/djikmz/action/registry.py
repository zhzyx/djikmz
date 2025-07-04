ACTION_REGISTRY = {}

def register_action(action_cls):
    def warpper(cls):
        ACTION_REGISTRY[action_cls] = cls
        return cls
    return warpper