def bit_counter():

    count = 0

    for i in range(1000000):
        count += f'{i:b}'.count('1')

    print(count)


if __name__ == '__main__':
    bit_counter()
