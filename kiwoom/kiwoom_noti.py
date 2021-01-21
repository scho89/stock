import os
import curses

from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errorCode import *
from config.kiwoomType import *
from PyQt5.QtTest import *

#import smtplib, ssl
from etc.colors import *


### Curses 변수
class Colors:
    BLUE = 2
    RED = 3
    IBLUE = 4
    IRED = 5
    GREEN = 6
       
win = curses.initscr()
win.clear()
curses.curs_set(False)
curses.start_color()

curses.init_pair(2,curses.COLOR_CYAN,curses.COLOR_BLACK)
curses.init_pair(3,curses.COLOR_RED,curses.COLOR_BLACK)
curses.init_pair(4,curses.COLOR_BLACK,curses.COLOR_CYAN)
curses.init_pair(5,curses.COLOR_BLACK,curses.COLOR_RED)
curses.init_pair(6,curses.COLOR_GREEN,curses.COLOR_BLACK)

color = Colors()


class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        print("Kiwoom 클래스 입니다.")
        win.addstr("Kiwoom 클래스 입니다."+"\n")
        win.refresh()

        self.realType = RealType()
        self.fcolor = BColors()
                
        ###### Event loops
        self.login_event_loop = None
        self.detail_account_info_event_loop = None
        self.detail_account_mystock_event_loop = None
        self.detail_account_mystock_event_loop = QEventLoop()
        self.calculator_event_loop = QEventLoop()    
        ########

        #### Variables
        self.account_num = None
        self.use_money = 0
        self.use_money_rate = 0.5 #예수금 사용 비율
        self.stock_counts = 2 # 거래할 종목 수
        self.account_stock_dict ={}
        self.request_waiting_time = 3600 # 일봉 데이터 요청 시 딜레이

        

        #### 전광판용 변수
        self.noti_file = 'C:/stock/files/noti_stocks.txt'
        self.my_price = None
        self.my_count = None 
        self.hoga_chang ={}
        self.screen_board = "8000"
        
        
        self.current_monitoring = None
        self.current_price = None
        self.current_quantity = None
        self.high_price = None
        self.low_price = None
        self.start_price = None


        # self.port = 587  # For starttls
        # self.smtp_server = "outlook.office365.com"
        # self.sender_email = "bp3@kor1.onmicrosoft.com"
        # self.receiver_email = "cho@kor1.onmicrosoft.com"
        # self.password = ""

        ###########

        self.calcul_data = [] # 종목 분석을 위한 데이터 저장용
        self.portfolio_stock_dict={}
        #### Screen number
        self.screen_my_info = "2000"
        self.screen_chart_data = "4000"
        self.screen_real_stock="5000" # 종목별 할당할 스크린 번호
        self.screen_meme_stock="6000" # 종목별 할당할 주문용 스크린 번호
        self.screen_start_stop_real ="1000" #장 시작여부 확인
        self.screen_hoga ="7000"


        ######################

        self.get_ocx_instance()
        self.event_slots()
        self.realtime_event_slots()

        ####

        self.signal_login_commConnect()
        self.get_account_info()
       # self.detail_account_info()
       # self.detail_account_mystock()
        

        #self.read_code()
        self.read_my_stock()
        #self.screen_number_setting()

        self.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen_start_stop_real, '',self.realType.REALTYPE['장시작시간']['장운영구분'],'0') #장 시작 여부

        # for code in self.portfolio_stock_dict.keys():
        #     screen_num = self.portfolio_stock_dict[code]['스크린번호']
        #     fids = self.realType.REALTYPE['주식체결']['체결시간']
        #     self.dynamicCall("SetRealReg(QString, QString, QString, QString)", screen_num, code,fids,'1') 
        #     print("실시간 등록 : %s, 스크린번호: %s, fid번호: %s" %(code,screen_num, fids))

            
        # ######### 호가 / 잔량 가져오기
        # for code in self.portfolio_stock_dict.keys():
        #     screen_num = self.portfolio_stock_dict[code]['호가용스크린번호']
        #     fids = self.realType.REALTYPE['주식호가잔량']['매도호가1']
        #     self.dynamicCall("SetRealReg(QString, QString, QString, QString)", screen_num, code,fids,'1')
        #     print("실시간 등록 : %s, 스크린번호: %s, fid번호: %s" %(code,screen_num, fids))



    def read_my_stock(self):
        
        f = open(self.noti_file,'r',encoding='utf8')
        noti_txt = f.readlines()
        f.close()

        for line in noti_txt:
            if line != "" and not line.startswith("#"):
                stock_data = line.split("\t")
                stock_code = stock_data[0]
                stock_name = stock_data[1]
                self.my_price = int(stock_data[2])
                self.my_count = int(stock_data[3]) 


        if not self.current_monitoring == stock_code:
            self.current_monitoring = stock_code
            win.clear()
            self.dynamicCall("SetRealRemove(QString, QString)",self.screen_board,self.current_monitoring)
            win.addstr("실시간 등록 해제 : %s, 스크린번호: %s \n" %(self.current_monitoring,self.screen_board))
            self.dynamicCall("SetRealRemove(QString, QString)",self.screen_hoga,self.current_monitoring)
            win.addstr("실시간 등록 해제 : %s, 스크린번호: %s \n" %(self.current_monitoring,self.screen_hoga))


            #시세 등록
            fids = self.realType.REALTYPE['주식체결']['체결시간']
            self.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen_board, stock_code,fids,'0') 
            print("실시간 등록 : %s, 스크린번호: %s, fid번호: %s" %(stock_code,self.screen_board, fids))
            win.addstr("실시간 등록 : %s, 스크린번호: %s, fid번호: %s \n" %(stock_code,self.screen_board, fids))
                
            #호가 / 잔량 가져오기
            fids = self.realType.REALTYPE['주식호가잔량']['매도호가1']
            self.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen_hoga, stock_code,fids,'0')
            print("실시간 등록 : %s, 스크린번호: %s, fid번호: %s" %(stock_code,self.screen_hoga, fids))
            win.addstr("실시간 등록 : %s, 스크린번호: %s, fid번호: %s \n" %(stock_code,self.screen_hoga, fids))
            win.refresh()
            
            
            

    def print_hoga_chang(self,hoga_chang,hoga_size=5,bin_n=50,marker='-'):
        start_row = 3

        if hoga_size not in range(1,11):
            hoga_size = 5
        print("호가창 출력부분 / print_hoga_chang")
        find_max = []
        for i in range(hoga_size,0,-1):
            find_max.append(hoga_chang[f'매도{i}'][1])
            find_max.append(hoga_chang[f'매수{i}'][1])           

        max_quan = max(find_max)
        bin_size = max_quan // bin_n

        for i in range(hoga_size,0,-1):

            #매도호가 표시
            if self.my_price == hoga_chang[f'매도{i}'][0]:
                win.addstr(start_row+hoga_size-i,0,f'{hoga_chang[f"매도{i}"][0]:,}:',curses.color_pair(color.GREEN))

            else:
                win.addstr(start_row+hoga_size-i,0,f'{hoga_chang[f"매도{i}"][0]:,}:')  # 35,000:


            win.addstr(f'{hoga_chang[f"매도{i}"][1]:12,}:') # 35,000:  12,124,123:
            graph_length = hoga_chang[f"매도{i}"][1] // bin_size

            if not marker == ' ':                       
                #print(self.fcolor.CYAN,marker*graph_length,self.fcolor.RESET) # 35,000: 12,123,123:----------------------------------
                win.addstr(marker*graph_length,curses.color_pair(color.BLUE)) # 35,000: 12,123,123:----------------------------------
            else:
                win.addstr(marker*graph_length,curses.color_pair(color.IBLUE))

        win.addstr(start_row+hoga_size,0,'-'*60)

        for i in range(1,1+hoga_size):
            #매수호가 표시
            if self.my_price == hoga_chang[f'매수{i}'][0]:
                win.addstr(start_row+hoga_size+i,0,f'{hoga_chang[f"매수{i}"][0]:,}:',curses.color_pair(color.GREEN))

            else:
                win.addstr(start_row+hoga_size+i,0,f'{hoga_chang[f"매수{i}"][0]:,}:')  # 35,000:

            win.addstr(f'{hoga_chang[f"매수{i}"][1]:12,}:') # 35,000:  12,124,123:
            graph_length = hoga_chang[f"매수{i}"][1] // bin_size
            
            if not marker == ' ':                       
                win.addstr(marker*graph_length,curses.color_pair(color.RED)) # 35,000: 12,123,123:----------------------------------

            else:
                win.addstr(marker*graph_length,curses.color_pair(color.IRED))

        win.addstr(start_row+1+hoga_size*2,0,'\n{0:,} / {1:,} / '.format(hoga_chang['총매도'],hoga_chang['총매수']))
        total_buy_sell_ratio = hoga_chang['총매수']/hoga_chang['총매도']

        if total_buy_sell_ratio > 1:
            win.addstr(f'{total_buy_sell_ratio:,.2f}',curses.color_pair(color.RED))
        else :
            win.addstr(f'{total_buy_sell_ratio:,.2f}',curses.color_pair(color.BLUE))
            
        win.addstr("\n\n")



        

    def get_ocx_instance(self):
        self.setControl('KHOPENAPI.KHOpenAPICtrl.1')


    def event_slots(self):
        self.OnEventConnect.connect(self.login_slot)
        self.OnReceiveTrData.connect(self.trdata_slot)

    def realtime_event_slots(self):
        self.OnReceiveRealData.connect(self.realtime_data_slot)


    def login_slot(self,errCode):
        print(errCode)
        print(errors(errCode))
        win.addstr(str(errCode)+"\n")
        win.addstr(str(errors(errCode))+"\n")
        win.refresh()
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
        self.dynamicCall("CommRqData(String, String, int, String)","예수금상세현황요청","opw00001","0",self.screen_my_info)

        self.detail_account_info_event_loop = QEventLoop()
        self.detail_account_info_event_loop.exec_()


    def detail_account_mystock(self,sPrevNext="0") :
        print("계좌평가 잔고내역 요청 부분")
        self.dynamicCall("SetInputValue(String, String)","계좌번호",self.account_num)
        self.dynamicCall("SetInputValue(String, String)","비밀번호","0000")
        self.dynamicCall("SetInputValue(String, String)","비밀번호입력매체구분","00")
        self.dynamicCall("SetInputValue(String, String)","조회구분","2")
        self.dynamicCall("CommRqData(String, String, int, String)","계좌평가잔고내역요청","opw00018",sPrevNext,self.screen_my_info)

        
        self.detail_account_mystock_event_loop.exec_()

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

            self.use_money = int(deposit) * self.use_money_rate
            self.use_money = self.use_money * self.stock_counts




            ok_deposit = self.dynamicCall("GetCommData(String, String, int, String)",sTrCode,sRQName,0, "출금가능금액")
            print("출금가능금액 %s"% int(ok_deposit))

            joomoon = self.dynamicCall("GetCommData(String, String, int, String)",sTrCode,sRQName,0, "주문가능금액")
            print("주문가능금액 %s"% int(joomoon))

            self.detail_account_info_event_loop.exit()

        elif sRQName == "계좌평가잔고내역요청":
            total_buy_money = self.dynamicCall("GetCommData(String, String, int, String)",sTrCode,sRQName,0, "총매입금액")
            total_buy_money_result = int(total_buy_money)
            print("총 매입금액 %s" %total_buy_money_result)

            total_profit_loss_rate = self.dynamicCall("GetCommData(String, String, int, String)",sTrCode,sRQName,0, "총수익률(%)")
            total_profit_loss_rate_result = float(total_profit_loss_rate)
            print("총 수익률 %s" %total_profit_loss_rate_result)

            rows = self.dynamicCall("GetRepeatCnt(QString, QString)",sTrCode,sRQName)
            cnt = 0
            for i in range(rows):
                stock_code = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode,sRQName,i,"종목번호")
                stock_name = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode,sRQName,i,"종목명")                
                stock_margin = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode,sRQName,i,"평가손익")
                stock_profit = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode,sRQName,i,"수익률(%)")
                stock_buy_price = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode,sRQName,i,"매입가")
                stock_quntity = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode,sRQName,i,"보유수량")
                stock_avail_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode,sRQName,i,"매매가능수량")
                stock_total_cost = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode,sRQName,i,"수수료합")

                stock_code = stock_code.strip()[1:]
                stock_name = stock_name.strip()
                stock_margin = int(stock_margin.strip())
                stock_profit = float(stock_profit.strip())
                stock_buy_price = int(stock_buy_price.strip())
                stock_quntity = int(stock_quntity.strip())
                stock_avail_quantity = int(stock_avail_quantity.strip())
                stock_total_cost = int(stock_total_cost.strip())

                if stock_code in self.account_stock_dict:
                    pass
                else:
                    self.account_stock_dict[stock_code]={}
                    self.account_stock_dict[stock_code]['종목명'] = stock_name
                    self.account_stock_dict[stock_code]['평가손익'] = stock_margin
                    self.account_stock_dict[stock_code]['수익률(%)'] = stock_profit
                    self.account_stock_dict[stock_code]['매입가'] = stock_buy_price
                    self.account_stock_dict[stock_code]['보유수량'] = stock_quntity
                    self.account_stock_dict[stock_code]['매매가능수량'] =stock_avail_quantity
                    self.account_stock_dict[stock_code]['수수료합'] = stock_total_cost

                    cnt+=1
            print("계좌에 가지고 있는 종목 수 : %s" %cnt)
            print(self.account_stock_dict)

            if sPrevNext =="2":
                self.detail_account_mystock(sPrevNext="2")
            else:
                self.detail_account_mystock_event_loop.exit()

        elif sRQName == "주식일봉차트조회":
            
            code = self.dynamicCall("GetCommData(QString, QString, int, QString)",sTrCode, sRQName,0,"종목코드")
            code = code.strip()
            print("%s 일봉데이터 요청"% code)

            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)",sTrCode,sRQName)
            print("%s 일 봉 조회 완료" % cnt)

            for i in range(cnt) :
                data = []
                current_price = self.dynamicCall("GetCommData(QString, QString, int , QString)",sTrCode, sRQName,0,"현재가")
                trading_volume = self.dynamicCall("GetCommData(QString, QString, int , QString)",sTrCode, sRQName,0,"거래량")
                trading_value = self.dynamicCall("GetCommData(QString, QString, int , QString)",sTrCode, sRQName,0,"거래대금")
                trading_date = self.dynamicCall("GetCommData(QString, QString, int , QString)",sTrCode, sRQName,0,"일자")
                start_price= self.dynamicCall("GetCommData(QString, QString, int , QString)",sTrCode, sRQName,0,"시가")
                high_price= self.dynamicCall("GetCommData(QString, QString, int , QString)",sTrCode, sRQName,0,"고가")
                low_price= self.dynamicCall("GetCommData(QString, QString, int , QString)",sTrCode, sRQName,0,"저가")
                end_price= self.dynamicCall("GetCommData(QString, QString, int , QString)",sTrCode, sRQName,0,"전일종가")
                
                data.append("")
                data.append(current_price.strip())
                data.append(trading_volume.strip())
                data.append(trading_value.strip())
                data.append(trading_date.strip())
                data.append(start_price.strip())
                data.append(high_price.strip())
                data.append(low_price.strip())
                data.append(end_price.strip())
                data.append("")

                self.calcul_data.append(data.copy())

            print(self.calcul_data)

            if sPrevNext == "2":
                self.day_kiwoom_db(code=code,sPrevNext=sPrevNext)

            else:
                self.calculator_event_loop.exit()



    def get_code_list_by_market(self, market_code):
        # 
        # return stock code list
        # 
        
        code_list = self.dynamicCall("GetCodeListByMarket(QString)",market_code)
        code_list = code_list.split(";")[:-1]

        return code_list


    def calculator_fnc(self):
        code_list = self.get_code_list_by_market("10")
        print("코스닥 종목 수 %s" %len(code_list))

        for idx,code in enumerate(code_list):
            self.dynamicCall("DisconnectRealData(QString)",self.screen_chart_data)
            print("%s / %s : KOSDAQ stock code : %s is updating..."%(idx+1,len(code_list),code))
            
            self.day_kiwoom_db(code=code)

    def day_kiwoom_db(self, code=None, date=None, sPrevNext = "0"):

        QTest.qWait(self.request_waiting_time)

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")

        if date != None:
            self.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)

        self.dynamicCall("CommRqData(QString, QString, int, QString)","주식일봉차트조회","opt10081",sPrevNext,self.screen_chart_data)
        self.calculator_event_loop.exec_()


    def read_code(self):
        if os.path.exists(self.noti_file):
            f = open(self.noti_file,"r",encoding="utf8")

            lines = f.readlines()
            for line in lines:

                if line !="":
                    ls = line.split("\t")

                    stock_code = ls[0]
                    stock_name = ls[1]
                    stock_price = abs(int(ls[2].strip()))

                    self.portfolio_stock_dict.update({stock_code:{"종목명":stock_name,"현재가":stock_price}})
            print(self.portfolio_stock_dict)    
            f.close()

    def screen_number_setting(self):
        screen_overwrite=[]

        #계좌평가잔고내역에 있는 종목
#        for code in self.account_stock_dict.keys():
#            if code not in screen_overwrite:
#                screen_overwrite.append(code)

        #미체결에 있는 종목들
        #for order_number in 

        
        #포트폴리오에 있는 종목
        for code in self.portfolio_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)


        #스크린번호 할당
        cnt = 0
        for code in screen_overwrite:
            temp_screen = int(self.screen_real_stock)
            meme_screen = int(self.screen_meme_stock)
            hoga_screen = int(self.screen_hoga)

            if (cnt%50) == 0:
                temp_screen += 1
                self.screen_real_stock = str(temp_screen)
                meme_screen +=1
                self.screen_meme_stock = str(meme_screen)
                hoga_screen +=1
                self.screen_hoga = str(hoga_screen)

            if code in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict[code]["스크린번호"]=str(self.screen_real_stock)
                self.portfolio_stock_dict[code]["주문용스크린번호"]=str(self.screen_meme_stock)
                self.portfolio_stock_dict[code]["호가용스크린번호"]=str(self.screen_hoga)

            elif code not in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict[code]={}
                self.portfolio_stock_dict[code]["스크린번호"]=str(self.screen_real_stock)
                self.portfolio_stock_dict[code]["주문용스크린번호"]=str(self.screen_meme_stock)
                self.portfolio_stock_dict[code]["호가용스크린번호"]=str(self.screen_hoga)

            cnt+=1

        print(self.portfolio_stock_dict)

    def realtime_data_slot(self,sCode,sRealType,sRealData):

        if sRealType == "장시작시간":
            fid = self.realType.REALTYPE['장시작시간']['장운영구분']
            value = self.dynamicCall("GetCommRealData(QString, int)",sCode,fid)

            if value =='0':
                print('장 시작 전')
                win.addstr('장 시작 전')
                
            elif value =='3':
                print('장 시작')
                win.addstr('장 시작')
                
            elif value =='2':
                print('장 종료 / 동시호가')
                win.addstr('장 종료 / 동시호가')
            elif value =='4':
                print('3시30분 장 종료')            
                win.addstr('3시30분 장 종료') 
            else:
                print('그외.......... 한밤중인가?')

            win.refresh()

        elif sRealType == "주식체결":
            current_price_fid = self.realType.REALTYPE['주식체결']['현재가']
            trade_quantity_fid = self.realType.REALTYPE['주식체결']['거래량']
            high_price_fid = self.realType.REALTYPE['주식체결']['고가']
            low_price_fid = self.realType.REALTYPE['주식체결']['저가']
            start_price_fid = self.realType.REALTYPE['주식체결']['시가']

            self.current_price = abs(int(self.dynamicCall("GetCommRealData(QString, int)",sCode,current_price_fid)))
            self.current_quantity = abs(int(self.dynamicCall("GetCommRealData(QString, int)",sCode,trade_quantity_fid)))
            self.high_price = abs(int(self.dynamicCall("GetCommRealData(QString, int)",sCode,high_price_fid)))
            self.low_price = abs(int(self.dynamicCall("GetCommRealData(QString, int)",sCode,low_price_fid)))
            self.start_price = abs(int(self.dynamicCall("GetCommRealData(QString, int)",sCode,start_price_fid)))

        elif sRealType =="주식호가잔량":
       

            for i in range(1,11):
                self.hoga_chang[f'매도{i}'] = [
                    abs(int((self.dynamicCall("GetCommRealData(QString, int)",sCode,self.realType.REALTYPE[sRealType][f'매도호가{i}'])))),
                    abs(int((self.dynamicCall("GetCommRealData(QString, int)",sCode,self.realType.REALTYPE[sRealType][f'매도호가수량{i}']))))
                ] 
                self.hoga_chang[f'매수{i}'] = [
                    abs(int((self.dynamicCall("GetCommRealData(QString, int)",sCode,self.realType.REALTYPE[sRealType][f'매수호가{i}'])))),
                    abs(int((self.dynamicCall("GetCommRealData(QString, int)",sCode,self.realType.REALTYPE[sRealType][f'매수호가수량{i}']))))
                ]

            sell_total_quan = abs(int((self.dynamicCall("GetCommRealData(QString, int)",sCode,self.realType.REALTYPE[sRealType]['매도호가총잔량']))))    
            buy_total_quan = abs(int((self.dynamicCall("GetCommRealData(QString, int)",sCode,self.realType.REALTYPE[sRealType]['매수호가총잔량']))))

            self.hoga_chang['총매도'] = sell_total_quan
            self.hoga_chang['총매수'] = buy_total_quan
            print(self.hoga_chang)
        #메모장에서 감시 종목 읽어오기
        self.read_my_stock()

        try:
            #os.system('cls')
            win.clear()

            #내 주가 현황
            win.addstr("{0:,}: {1:,} / {2:,}\n".format(self.start_price,self.high_price,self.low_price))

            #색 설정

            my_margin = (self.current_price-self.my_price)*self.my_count
            my_gap = self.current_price-self.my_price
            my_profit =100*(self.current_price/self.my_price-1)

            # if current_price > start_price : print(self.fcolor.RED,format(current_price,','),self.fcolor.RESET,end=" ")
            # elif current_price < start_price : print(self.fcolor.CYAN,format(current_price,','),self.fcolor.RESET,end=" ")
            win.addstr(f'{self.current_price:,} ')       
            
            if my_gap > 0 : win.addstr(f'{my_gap} ',curses.color_pair(color.RED))
            elif my_gap < 0 :win.addstr(f'{my_gap} ',curses.color_pair(color.BLUE))
            
            if my_profit > 0 : win.addstr(f'{my_profit:.2f} ',curses.color_pair(color.RED))
            elif my_profit < 0 : win.addstr(f'{my_profit:.2f} ',curses.color_pair(color.BLUE))

            if my_margin > 0 : win.addstr(f'{my_margin:,} ',curses.color_pair(color.RED))
            elif my_margin < 0 : win.addstr(f'{my_margin:,} ',curses.color_pair(color.BLUE))

            win.addstr(f'{self.current_quantity}')
            win.addstr("\n\n")
            #print(format(current_price,','),my_gap,format(my_profit,".2f"), format(my_margin,',',),current_quantity)

            self.print_hoga_chang(self.hoga_chang,hoga_size=10)

            win.refresh()

        except Exception as e :

            print(e)
            
