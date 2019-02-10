def count_bits():

    count = 0
    A = 5

    for i in range(A * A):
        count += int(bin(i).count('1'))

    print(count)


if __name__ == '__main__':
    count_bits()
