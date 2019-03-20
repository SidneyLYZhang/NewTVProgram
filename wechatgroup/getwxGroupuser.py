import itchat
import xlsxwriter
import os

def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)
    else:
        print('--- This Path exists! ---\n')
    return('OK')

if __name__ == '__main__':
    thePath = '~/Desktop/Images/groupuser/'
    mkdir(thePath)
    itchat.auto_login(True)
    mpsList=itchat.get_chatrooms(update=True)
    for it in mpsList:
        chatroomName=it['NickName']
        chatrooms = itchat.search_chatrooms(name=chatroomName)
        chatplace = itchat.update_chatroom(chatrooms[0]['UserName'])
        workbook = xlsxwriter.Workbook(thePath + chatroomName + '.xlsx')
        worksheet = workbook.add_worksheet()
        rows = 0
        for f in chatplace['MemberList']:
            f['Uin']
            worksheet.write_string(rows,0,f['NickName'])
            worksheet.write_string(rows,1,f['DisplayName'])
            worksheet.write_string(rows,2,f['UserName'])
            rows += 1
        workbook.close()
    

        