def maskify(cc):

    # replace spaces & dashes
    # ensure uppercase for consistency

    cc = cc.replace('-', '').replace(' ', '').upper()

    # make an exception for input with <= 6 characters

    if len(cc) <= 6:
        print(cc)
    print(cc)
    # else:
    #     print((len(cc) - 4) * "#" + cc[1:-4])


if __name__ == '__main__':
    maskify('999999')
    maskify('1111-2222-3333-4444')
    maskify('1111222233334444')
    maskify('1111 2222 3333 4444')
    maskify('ABCD-EFGH-IJKL-MNOP')
    maskify('1A2B2D3E4F5G6H7k')
