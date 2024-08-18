"""
Develop a strategy that takes a long position when the Accumulation/Distribution Line 
is rising and the RSI is below 30. 
Take a short position when the Accumulation/Distribution Line is falling and the RSI is above 70.
"""

from blueshift.api import (
    symbol,
    schedule_function,
    date_rules,
    time_rules,
    get_datetime,
    order_target_percent
)

import numpy as np
import talib
from datetime import datetime,time

def initialize(context):

    context.security=[symbol('ESCORTS'),symbol('GMRINFRA'),symbol('GLENMARK'),symbol('GODREJCP'),symbol('GODREJPROP'),symbol('GRANULES'),symbol('GRASIM'),symbol('GUJGASLTD')]

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
            adline = talib.AD(df['high'], df['low'], df['close'], df['volume'])
            prev=adline[-2]
            cur=adline[-1]
            trsi=talib.RSI(df['close'],timeperiod=30)
            rsi=trsi[-1]
            if (context.current_position[i]==0):
                if (rsi<=30) and (cur>prev):
                    order_target_percent(context.security[i],1/len(context.security))
                    context.current_position[i]=1
                    context.entryprice[i]=cp 
                    context.sl[i]=context.entryprice[i]*0.85
                    context.tp[i]=context.entryprice[i]*1.15
                
                elif (rsi>=70) and (cur<prev):
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
                
                elif cp>context.entryprice[i] and cp<context.tp[i]:
                    context.sl[i]=cp*0.85
            
            elif (context.current_position[i]==-1):
                if cp<=context.tp[i] or cp>=context.sl[i]:
                    order_target_percent(context.security[i],0)
                    context.current_position[i]=0
                    context.entryprice[i]=0
                    context.sl[i]=0
                    context.tp[i]=0
                
                elif cp<context.entryprice[i] and cp>context.tp[i]:
                    context.sl[i]=cp*1.15
    
    else:
        pass

def square_off(context,data):
    for i in range(0,len(context.security)):
        order_target_percent(context.security[i],0)
        context.current_position[i]=0
        context.entryprice[i]=0
        context.sl[i]=0
        context.tp[i]=0


                

                    

