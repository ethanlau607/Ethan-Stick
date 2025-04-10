from machine import Pin, I2C,PWM
from ssd1306_i2c_flag import SSD1306_I2C_FLAG
import time,math


beeper=PWM(Pin(15,Pin.OUT), freq=1000, duty=0)

melody = {"Little Star":"1=1=5=5=6=6=5=__4=4=3=3=2=2=1=__5=5=4=4=3=3=2=__5=5=4=4=3=3=2=__1=1=5=5=6=6=5=__4=4=3=3=2=2=1="}

tones = {
    '1=': 523,
    '1+':554,
    
    '2-':554,
    '2=': 587,
    '2+':622,
    
    '3-':622,
    '3=': 659,
    
    '4=': 698,
    '4+':740,
    
    '5-':740,
    '5=': 784,
    '5+':830,
    
    '6-':830,
    '6=': 880,
    '6+':932,
    
    '7-':932,
    '7=': 988,
    
    '8=': 1046,
    '8+':1108,
    
    '9-':1108,
    '9=': 1175,
    '9+':1245,
    
    '10-':1245,
    '10=': 1318,
    
    '11=': 1397,
    '11+': 1480,
    
    '12-':1480,
    '12=': 1568,
    '12+':1661,
    
    '13-':1661,
    '13=': 1760,
    '13+':1865,
    
    '14-':1865,
    '14=': 1976,
    '__': 0
}


# 初始化按鈕
button1 = Pin(12, Pin.IN, Pin.PULL_UP) 
button2 = Pin(13, Pin.IN, Pin.PULL_UP) 
button3 = Pin(14, Pin.IN, Pin.PULL_UP)  # 選擇/退格按鈕

page="home"
home_options = ["Calculator","Guess Number","Pi Game","Music"]

home_displaying_index = 0
# 指定 SCL 在 5 號腳位 (D1), SDA 在 4 號腳位 (D2)
i2c = I2C(scl=Pin(5), sda=Pin(4))

# 指定寬 128 像素, 高 64 像素, 以及要使用的 I2C 物件
oled = SSD1306_I2C_FLAG(128, 64, i2c)


def play(beeper, melody, duty = 10):
    i = 0
    keep = False
    while i  < len(melody):
        if melody[i] == '(':
            i += 1
            keep = True
            continue
        elif melody[i] == ')':
            i += 1
            keep = False

            # 连音结束后稍微停顿下
            beeper.duty(0)
            time.sleep_ms(75)
            continue
        if melody[i+1]not in ["=","+","-","_"]:
            tone, level = melody[i]+melody[i+1], melody[i+2]
            i+=3
        else:
            tone, level = melody[i], melody[i+1]
        
            i += 2
        freq = tones[tone+level]
        if freq:
            beeper.init(duty=duty, freq=freq)
        else:
            beeper.duty(0)  # 空拍时静音

        # 停顿一下 （四四拍每秒两个音，每个音节中间稍微停顿一下）
        time.sleep_ms(150)
        if not keep:
            beeper.duty(0)  # 设备占空比为0，即不上电
        time.sleep_ms(75)

# 新增顯示內容列表
display_lines = ["", "", "", ""]  # 四行顯示內容
def update_display():
    oled.fill(0)
    for i, line in enumerate(display_lines):
        oled.text(line, 0, i * 16)  # 每行間隔16像素
    oled.show()

def music():
    time.sleep(0.2)
    global button1, button2, button3, page,display_lines
    music_options = ["Little Star","Birthday Song", "Exit"]
    music_index=0
    while True:
        if page == 'music':
            display_lines[0] = 'Music:'
            display_lines[1] = '> ' + music_options[music_index]
            display_lines[2], display_lines[3] = "", ""
            update_display()
            if button1.value() == 0:
                music_index += 1
                music_index %= len(music_options)
                time.sleep(0.2)
            elif button2.value() == 0:
                music_index -= 1
                music_index %= len(music_options)
                time.sleep(0.2)
            elif button3.value() == 0:
                if music_options[music_index] == "Exit":
                    page = "home"
                    main()
                else:
                    stop_playing = False
                    def play_with_interrupt():
                        nonlocal stop_playing
                        i = 0
                        keep = False
                        while i < len(melody[music_options[music_index]]) and not stop_playing:
                            if melody[music_options[music_index]][i] == '(':
                                i += 1
                                keep = True
                                continue
                            elif melody[music_options[music_index]][i] == ')':
                                i += 1
                                keep = False
                                beeper.duty(0)
                                time.sleep_ms(75)
                                continue
                            if melody[music_options[music_index]][i+1] not in ["=","+","-","_"]:
                                tone, level = melody[music_options[music_index]][i]+melody[music_options[music_index]][i+1], melody[music_options[music_index]][i+2]
                                i+= 3
                            else:
                                tone, level = melody[music_options[music_index]][i], melody[music_options[music_index]][i+1]
                                i+= 2
                            freq = tones[tone+level]
                            if freq:
                                beeper.init(duty=10, freq=freq)
                            else:
                                beeper.duty(0)
                            time.sleep_ms(150)
                            if not keep:
                                beeper.duty(0)
                            time.sleep_ms(75)
                            if button3.value() == 0:
                                stop_playing = True
                                time.sleep(0.2)
                                beeper.duty(0)
                                beeper.deinit()  # 停止播放并释放资源
                                page = 'music'
                                return  # 直接返回音乐选择界面
                                break

                    play_with_interrupt()
                    if stop_playing:
                        beeper.duty(0)
                        page = "music"
                        main(music())
                time.sleep(0.2)
def pi_game():
    time.sleep(0.2)
    global button1, button2, button3, page
    pi_digits = '3141592653589793238462643383279502884197169399375105820974944592307816406286208998628034825342117067'
    current_index = 0
    pi_index=0
    start_time = time.ticks_ms()
    correct_count = 0
    while True:
        if page == 'PiGame':
            display_lines[0] = 'Pi Game:'
            display_lines[1] = 'Enter digit ' + str(current_index + 1)
            display_lines[2] = 'Correct: ' + str(correct_count)
            display_lines[3] = 'Time: ' + str((time.ticks_ms() - start_time) // 1000) + 's'
            update_display()
            if button1.value() == 0:
                if current_index!=0:
                    current_index -= 1
                else:current_index=8
                time.sleep(0.2)
            if button2.value() == 0:
                if current_index!=8:
                    current_index += 1
                else:current_index=0
                time.sleep(0.2)
            if button3.value() == 0:
                if str(current_index+1) == pi_digits[pi_index]:
                    pi_index+=1
                    correct_count += 1
                    time.sleep(0.2)
                    if pi_index == len(pi_digits):
                        display_lines[0] = 'You Win!'
                        display_lines[1] = 'Your Score:'+ str(correct_count)
                        display_lines[2] = 'Press any button'
                        display_lines[3] = 'to continue'
                        update_display()
                        time.sleep(1)
                        while button1.value() and button2.value() and button3.value():
                            pass
                        page = 'home'
                        main()
                else:
                    display_lines[0] = 'Wrong!'
                    display_lines[1] = 'Correct: ' + str(correct_count)
                    display_lines[2] = 'Press any button'
                    display_lines[3] = 'to exit'
                    update_display()
                    time.sleep(1)
                    while button1.value() and button2.value() and button3.value():
                        pass
                    page = 'home'
                    main()
    
def GuessNum():
    time.sleep(0.2)
    global button1,button2,button3,page
    game_options = ["Start Game", "Exit"]
    game_index = 0
    while True:
        if page=="GuessNum":
            if button1.value()==0:
                game_index += 1
                game_index %= len(game_options)
                time.sleep(0.2)
            if button2.value()==0:
                game_index -= 1
                game_index %= len(game_options)
                time.sleep(0.2)
            if button3.value()==0:
                if game_options[game_index]=="Start Game":
                    time.sleep(0.2)
                    num = int((time.ticks_us()*math.pi % 98) + 2)  # 确保随机数在2到99之间
                    min_num=2
                    max_num=99
                    guess = 2
                    guess_num = [2]
                    while True:
                        display_lines[0] = "Guess Number:"
                        display_lines[1] = "Range: " + str(min_num) + "-" + str(max_num)
                        display_lines[2] = "Your Guess:"
                        display_lines[3] = "Exit" if guess_num and guess_num[-1] == 100 else str(guess_num[-1]) if guess_num else ""
                        # 移除長按button3退出的功能
                        update_display()
                        if button1.value()==0:
                            if guess == 99:
                                guess = 100
                            elif guess == 100:
                                guess = 2
                            else:
                                guess = (guess or min_num) + 1
                            guess_num.append(guess)
                            time.sleep(0.2)
                        if button2.value()==0:
                            if guess == 2:
                                guess = 100
                            elif guess == 100:
                                guess = 99
                            else:
                                guess = (guess or max_num) - 1
                            guess_num.append(guess)
                            time.sleep(0.2)
                        if button3.value()==0:
                            if game_options[game_index]=="Exit":
                                page = "home"
                                main()
                            if guess==100:
                                page = "home"
                                main()
                            if guess is not None:
                                if guess < num and min_num<guess:
                                    min_num = guess
                                elif guess > num and max_num>guess:
                                    max_num = guess
                                elif guess==num:
                                    while button1.value()==0 or button2.value()==0 or button3.value()==0:time.sleep(0.1)
                                    display_lines[0] = 'You Win!'
                                    display_lines[1] = 'Number was ' + str(num)
                                    display_lines[2] = 'Press any button'
                                    display_lines[3] = 'to continue'
                                    update_display()
                                    time.sleep(1)
                                    while button1.value() and button2.value() and button3.value():
                                        pass
                                    page = 'home'
                                    main()
                            
                            
                                    
                            time.sleep(0.2)
                elif game_options[game_index]=="Exit":
                    time.sleep(0.2)
                    page = "home"
                    main()
            display_lines[0] = "Guess Number:"
            display_lines[1] = "> " + game_options[game_index]
            display_lines[2], display_lines[3] = "", ""
            update_display()
            
def calc():
    time.sleep(0.2)
    global buuton1,button2,button3,page
    numbers = [str(i) for i in range(10)] + ["+", "-", "*", "/", "=", "C", "Exit"]  # 0-9 + 運算符 + 等於 + 清除 + 退出
    number_selected=0
    selected_thing=""
    calc_output=""
    while True:
        if page=="calc":
            if button1.value()==0:
                number_selected+=1
                number_selected%=len(numbers)
                time.sleep(0.2)
            if button2.value()==0:
                number_selected-=1
                number_selected%=len(numbers)
                time.sleep(0.2)
            if button3.value()==0:
                if numbers[number_selected].isdigit():
                    selected_thing += numbers[number_selected]
                    time.sleep(0.2)
                elif numbers[number_selected]=="=":
                    try:
                        calc_output = str(eval(selected_thing))
                    except:
                        calc_output = "Error"
                    time.sleep(0.2)
                elif numbers[number_selected] in ["+", "-", "*", "/"]:
                    selected_thing +=  numbers[number_selected] 
                    time.sleep(0.2)
                elif numbers[number_selected]=="C":
                    numbers = [str(i) for i in range(10)] + ["+", "-", "*", "/", "=", "C", "Exit"]
                    number_selected=0
                    selected_thing=""
                    calc_output=""
                    time.sleep(0.2)
                elif numbers[number_selected]=="Exit":
                    page="home"
                    main()
            display_lines[0]="Calculator:"
            display_lines[1]="In: "+selected_thing
            display_lines[2]="Selected: "+numbers[number_selected]
            display_lines[3]="Out: "+str(calc_output)
            update_display()
        
def main():
    time.sleep(0.2)
    global buuton1,button2,button3,page,home_options,display_lines,home_displaying_index
    while True:
        if page=="home":
            if button1.value()==0:
                
                home_displaying_index+=1
                home_displaying_index%=len(home_options)
                time.sleep(0.2)
            if button2.value()==0:
                
                home_displaying_index-=1
                home_displaying_index%=len(home_options)
                time.sleep(0.2)
            if button3.value()==0:
                if home_options[home_displaying_index]=="Calculator":
                    page="calc"
                    calc()
                    time.sleep(0.2)
                elif home_options[home_displaying_index]=="Guess Number":
                    page="GuessNum"
                    GuessNum()
                    time.sleep(0.2)
                elif home_options[home_displaying_index]=="Pi Game":
                    page="PiGame"
                    pi_game()
                    time.sleep(0.2)
                elif home_options[home_displaying_index]=="Music":
                    page="music"
                    music()
                    time.sleep(0.2)
            display_lines[0]="Home:"
            display_lines[1]="> "+home_options[home_displaying_index]
            display_lines[2],display_lines[3]="",""
            update_display()
beeper.deinit()
main()