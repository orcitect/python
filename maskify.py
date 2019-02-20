import re

regex = re.compile(r'\d+')


def maskify(cc):

    cc = cc.replace('-', '').replace(' ', '')

    if len(cc) <= 5:
        print(cc)
    else:
        sub = ''.join([(regex.sub('#', c)) for c in cc[1:-4]])
        new_cc = cc[0] + sub + cc[-4:]
        print(new_cc)


if __name__ == '__main__':
    maskify('123456')
    maskify('A12B2D3E4F586H7K')
