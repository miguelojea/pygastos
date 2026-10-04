def sum(x, y):
    return x + y


def incremented_numbers(x, y, z):
    if x < y and y < z:
        return True
    else:
        return False


class Increment:
    x = 0

    def _inc(cls):
        cls.x += 1
