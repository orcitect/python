def bit_counter(num):

    count = 0

    for i in range(num):
        count += f'{i:b}'.count('1')

    print(count)


if __name__ == '__main__':
    bit_counter(1000000)
