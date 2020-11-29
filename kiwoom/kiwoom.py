from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *



class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        print("Kiwoom 클래스 입니다.")

        ###### Event loops
        self.login_event_loop = None
        ########
        #### Variables

        self.account_num = None


        self.get_ocx_instance()
        self.event_slots()
        self.signal_login_commConnect()
        self.get_account_info()
        self.detail_account_info()

    def get_ocx_instance(self):
        self.setControl('KHOPENAPI.KHOpenAPICtrl.1')


    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)
        self.OnReceiveTrData.connect(self.trdata_slot)


    def login_slot(self,errCode):
        print(errCode)
        print(errors(errCode))

        self.login_event_loop.exit()

    def signal_login_commConnect(self):
        self.dynamicCall("CommConnect")

        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()


    def get_account_info(self):
        account_list = self.dynamicCall("GetLoginInfo(String)","ACCNO")
        self.account_num = account_list.split(";")[0]

        print("나의 보유 계좌번호 %a" % self.account_num)




    def detail_account_info(self):
        print("예수금을 요청하는 부분")
        self.dynamicCall("SetInputValue(String, String)","계좌번호",self.account_num)
        self.dynamicCall("SetInputValue(String, String)","비밀번호","0000")
        self.dynamicCall("SetInputValue(String, String)","비밀번호입력매체구분","00")
        self.dynamicCall("SetInputValue(String, String)","조회구분","2")
        self.dynamicCall("CommRqData(String, String, int, String)","예수금상세현황요청","opw00001","0","2000")


    def trdata_slot(self,sScrNo, sRQName,sTrCode,SRecordName,sPrevNext):
        '''
        :param sScrNo : 스크린번호
        :param sRQName: 요청에서 지은 이름
        :param sTrCode: 요청 id / tr코드
        :param sRecordName :사용안함
        :param sPrevNext: 다음 페이지 유무 ?
        '''

        if sRQName == "예수금상세현황요청":
            deposit = self.dynamicCall("GetCommData(String, String, int, String)",sTrCode,sRQName,0, "예수금")
            print('예수금 %s' % int(deposit))

            ok_deposit = self.dynamicCall("GetCommData(String, String, int, String)",sTrCode,sRQName,0, "출금가능금액")
            print(ok_deposit)

            joomoon = self.dynamicCall("GetCommData(String, String, int, String)",sTrCode,sRQName,0, "주문가능금액")
            print("주문가능금액 %s"% int(joomoon))