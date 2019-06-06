import os

def init_App(libs):
    try:
        os.system('python -m pip install --upgrade pip')
        for i in libs:
            os.system('python -m pip install -U ' + i)
        print('----------SUCCEEDED----------')
    except:
        print('**********ERROR**********')

if __name__ == '__main__':
    needLibs = ['six','re','toml','click','colorama','termcolor','pyfiglet','PyInquirer']
    init_App(needLibs)