import re


def maskify(cc):

    if len(cc) <= 6:
        print(cc)
    else:
        print((len(cc) - 4) * "#" + cc[1:-4])

    #print(cc.replace('-', '').replace(' ', ''))


if __name__ == '__main__':
    maskify('999999')
    maskify('1111-2222-3333-4444')
    maskify('1111222233334444')
    maskify('1111 2222 3333 4444')
    maskify('ABCD-EFGH-IJKL-MNOP')
    maskify('ABCD-EFGH-IJKL-MNOP')
