"""
Create a strategy that takes a long position when the Chaikin Oscillator is above zero and the MACD line is above the MACD signal line. 
Take a short position when the Chaikin Oscillator is below zero and the MACD line is below the MACD signal line.

"""

from blueshift.api import (
    symbol,
    schedule_function,
    date_rules,
    time_rules,
    get_datetime,
    order,
    order_target_percent
)

import talib
import numpy as np
from datetime import datetime,time

def initialize(context):

    context.security=[symbol('DLF'),symbol('DABUR'),symbol('DIVISLAB'),symbol('DEEPAKNTR'),symbol('DIXON'),symbol('EICHERMOT'),symbol('GAIL')]

    schedule_function(
        square_off,
        date_rule=date_rules.every_day(),
        time_rule=time_rules.market_close(minutes=2)
    )

def before_trading_start(context,data):
    
    context.current_position=np.zeros(len(context.security))
    context.entryprice=np.zeros(len(context.security))
    context.sl=np.zeros(len(context.security))
    context.tp=np.zeros(len(context.security))

def handle_data(context,data):
    ct=get_datetime()
    tz=ct.tzinfo
    st=datetime.combine(ct.date(),time(9,30),tzinfo=tz)
    et=datetime.combine(ct.date(),time(15,28),tzinfo=tz)
    if ct>st and ct<et:
        for i in range(0,len(context.security)):
            cp=data.current(context.security[i],'close')
            df=data.history(context.security[i],['open','high','close','low','volume'],30,'1m')
            macdline,macdsignal,macdhist=talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
            line=macdline[-1]
            signal=macdsignal[-1]
            tco = talib.ADOSC(df['high'], df['low'], df['close'], df['volume'], fastperiod=3, slowperiod=10)
            co=tco[-1]
            if (context.current_position[i]==0):
                if line>signal and co>0:
                    order_target_percent(context.security[i],1/len(context.security))
                    context.current_position[i]=0
                    context.entryprice[i]=cp 
                    context.sl[i]=context.entryprice[i]*0.85
                    context.tp[i]=context.entryprice[i]*1.15
                
                if line<signal and co<0:
                    order_target_percent(context.security[i],-1/len(context.security))
                    context.current_position[i]=-1
                    context.entryprice[i]=cp 
                    context.sl[i]=context.entryprice[i]*1.15
                    context.tp[i]=context.entryprice[i]*0.85
            
            elif (context.current_position[i]==1):
                if cp>=context.tp[i] or cp<=context.sl[i]:
                    order_target_percent(context.security[i],0)
                    context.current_position[i]=0
                    context.entryprice[i]=0
                    context.sl[i]=0
                    context.tp[i]=0
            
            elif (context.current_position[i]==-1):
                if cp<=context.tp[i] or cp>=context.sl[i]:
                    order_target_percent(context.security[i],0)
                    context.current_position[i]=0
                    context.entryprice[i]=0
                    context.sl[i]=0
                    context.tp[i]=0
    
    else:
        pass


def square_off(context,data):
    for i in range(0,len(context.security)):
        order_target_percent(context.security[i],0)
        context.current_position[i]=0
        context.entryprice[i]=0
        context.sl[i]=0
        context.tp[i]=0
