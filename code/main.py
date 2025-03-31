from machine import Pin, I2C
from ssd1306_i2c_flag import SSD1306_I2C_FLAG
import time,math


# 初始化按鈕
button1 = Pin(12, Pin.IN, Pin.PULL_UP) 
button2 = Pin(13, Pin.IN, Pin.PULL_UP) 
button3 = Pin(14, Pin.IN, Pin.PULL_UP)  # 選擇/退格按鈕

page="home"
home_options = ["Calculator","Guess Number","Pi Game"]

home_displaying_index = 0
# 指定 SCL 在 5 號腳位 (D1), SDA 在 4 號腳位 (D2)
i2c = I2C(scl=Pin(5), sda=Pin(4))

# 指定寬 128 像素, 高 64 像素, 以及要使用的 I2C 物件
oled = SSD1306_I2C_FLAG(128, 64, i2c)

# 新增顯示內容列表
display_lines = ["", "", "", ""]  # 四行顯示內容

def update_display():
    oled.fill(0)
    for i, line in enumerate(display_lines):
        oled.text(line, 0, i * 16)  # 每行間隔16像素
    oled.show()


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
               
            display_lines[0]="Home:"
            display_lines[1]="> "+home_options[home_displaying_index]
            display_lines[2],display_lines[3]="",""
            update_display()

main()