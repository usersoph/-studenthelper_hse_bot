
from telebot import *
from sympy import *
import os
import pandas as pd

import time


TOKEN = os.environ["BOT_TOKEN"]

ADMIN_ID = os.environ["ADMIN_ID"].strip()


sheet_mpr = os.environ["SHEET_MPR_ID"]
sheet_mpr_url = f'https://docs.google.com/spreadsheets/d/{sheet_mpr}/export?format=xlsx'
sheet_fin = os.environ["SHEET_FIN_ID"]
mat_mpr = os.environ["MAT_MPR_ID"]
mat_ess = os.environ["MAT_ESS_ID"]
mat_koll = os.environ["MAT_KOLL_ID"]

formulas =  { 'ess gr': (['семакт(тесты на семинарах)', 'дз', 'кр', 'экз'],
                         Matrix([S(24)/100, S(15)/100, S(21)/100, S(4)/10])),
              'zak gr': (['тесты лекция', 'активность', 'коллоквиум', 'экз'],
                         Matrix([S(2) / 10, S(2) / 10, S(3) / 10, S(3) / 10])),
              'inn gr': (['семакт + ср', 'итоговый тест'],
              Matrix([S(1) / 2, S(1) / 2])),
              'fin gr': (['аудиторная работа', 'постановочная дискуссия', 'тестирование'],
                         Matrix([S(333) / 1000, S(334) / 1000, S(333) / 1000]))
}
pics = {'ess gr': 'images/ess_formula.png',
        'zak gr': 'images/zakup_formula.png',
        'inn gr': 'images/inn_formula.png',
        'fin gr': 'images/fin_formula.png',
        }

user_data = {}

seen = {}



bot = TeleBot(TOKEN)

bot.set_my_commands([types.BotCommand('/start', 'главное меню')])
kb = types.ReplyKeyboardMarkup(resize_keyboard=True, is_persistent=True)
kb.add('главное меню')

for uid in os.environ.get("USER_IDS", " ").split(","):
    if uid.strip():
        uid = int(uid)
        try:
            chat = bot.get_chat(uid)
            seen[uid] = f'{chat.first_name} @{chat.username}'
        except Exception:
            seen[uid] = 'из списка'

@bot.message_handler(commands=['users'])
def users_list(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    if not seen:
        bot.send_message(message.chat.id, 'никого нет')
        return
    text = f'пользователей: {len(seen)}\n\n'
    for uid, info in seen.items():
        text += f'{info} (id {uid})\n'
    bot.send_message(message.chat.id, text)



@bot.message_handler(commands=['start'])
def welcome(message):
    user = message.from_user
    if user.id not in seen:
        seen[user.id] = f'{user.first_name} @{user.username}'
        bot.send_message(ADMIN_ID, f'новый пользователь: {seen[user.id]} (id {user.id})')

    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('ведомости', callback_data = 'vedomosti')
    btn2 = types.InlineKeyboardButton('накоп', callback_data = 'nakop')
    btn3 = types.InlineKeyboardButton('справочная', callback_data = 'email')
    btn4 = types.InlineKeyboardButton('материалы', callback_data = 'materials')
    btn5 = types.InlineKeyboardButton('курсовая', callback_data = 'kursach')
    btn6 = types.InlineKeyboardButton('полезные ссылки', callback_data = 'links')
    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    markup.row(btn4)
    markup.row(btn5)
    markup.row(btn6)
    bot.reply_to(message, 'привет, '
                          'выбирай тот раздел, который интересует 🗂️\n'
                          '\n'
                          '\nпользуясь этим ботом, вы принимаете, что пересылать материалы/контакты из этого бота другим людям(не студентам) - нельзя!\n'
                          '\nкак вы будете распоряжаться этой информацией - дело ваше :з', reply_markup=markup)

def is_menu(message):
    if message.text in ['/start','главное меню']:
        return True
    return False


@bot.callback_query_handler(func= lambda callback: True)
def callback_message(call):
    bot.answer_callback_query(call.id)
    markup = types.InlineKeyboardMarkup()

    if call.data == 'vedomosti':
        v1 = types.InlineKeyboardButton('мпр', url=f'https://docs.google.com/spreadsheets/d/{sheet_mpr}/edit')
        v2 = types.InlineKeyboardButton('упр фин', url=f'https://docs.yandex.ru/edit/d/{sheet_fin}')
        markup.row(v1, v2)
        bot.send_message(call.message.chat.id,'выбери ведомость, которая тебе нужна\nдля возврата в главное меню /start', reply_markup = markup)
    elif call.data == 'email':
        e1 = types.InlineKeyboardButton('учебка', callback_data = 'uchebka')
        e2 = types.InlineKeyboardButton('техподдержка', callback_data = 'tech')
        e3= types.InlineKeyboardButton('центр сервиса студент', callback_data='student')
        markup.row(e1)
        markup.row(e2)
        markup.row(e3)
        bot.send_message(call.message.chat.id, 'выбери контакт, который нужен\n'
                                               '\nдля возврата в главное меню /start', reply_markup=markup)
    elif call.data == 'uchebka':
        with open('images/uchebka1.png','rb') as photo:
            bot.send_photo(call.message.chat.id, photo,
                           caption= 'msbykova@hse.ru -- нажми чтобы скопировать\n'
                                    '\nдля возврата в главное меню /start' )
    elif call.data == 'tech':
        with open('images/tech.png','rb') as photo:
            bot.send_photo(call.message.chat.id, photo,
                           caption = 'digital@hse.ru -- если твоя проблема с приложением/почтой или лмсом '
                                     'helpexam@hse.ru -- если проблема с онлайн экзаменом (ставь Севостьянову в копию, если экзамен идет прям щас)\n'
                                     '\nдля возврата в главное меню /start')
    elif call.data == 'student':
        with open('images/student1.png', 'rb') as photo:
            bot.send_photo(call.message.chat.id, photo,
                           caption = 'studentcentre@hse.ru -- учти, что обычно справки итд делают от 3 до 5 дней, лучше вообще туда прийти лично\n'
                                     '\nдля возврата в главное меню /start')
    elif call.data == 'materials':
        m1 = types.InlineKeyboardButton('мпр', url=f'https://drive.google.com/drive/folders/{mat_mpr}')
        m2 = types.InlineKeyboardButton('эсс', url=f'https://disk.yandex.ru/d/{mat_ess}')
        m3 = types.InlineKeyboardButton('коллоквиум', url=f'https://drive.google.com/drive/folders/{mat_koll}')
        markup.row(m1, m2)
        markup.row(m3)
        bot.send_message(call.message.chat.id, 'выбери материалы, которые нужны\n'
                                               '\nдля возврата в главное меню /start', reply_markup=markup)
    elif call.data == 'kursach':
        with open('images/kursach.png','rb') as photo:
            bot.send_photo(call.message.chat.id, photo,
                           caption = 'сначала договорись с научным руководителем о теме (можно написать нескольким)!!!!\n'
                                     '\nтема есть : заявка с 02.11.26: https://confluence.hse.ru/x/bGP_Dg\n'
                                     'если темы нет : инициативная тема: https://confluence.hse.ru/x/ySdeDw\n'
                                     '\nдокументы: https://www.hse.ru/ba/gmu/internships\n'
                                     '\nвопросы: msbykova@hse.ru'
                                     '\n'
                                     '\nдля возврата в главное меню /start')
    elif call.data == 'links':
        l1 = types.InlineKeyboardButton('вшэ лмс',
                                        url='https://auth.hse.ru/adfs/oauth2/authorize?client_id=4403a646-2af8-42ba-a2b1-4f5a50a5b376&redirect_uri=https://smartedu.hse.ru/auth&response_type=token&response_mode=fragment')
        l2 = types.InlineKeyboardButton('вшэ старый сайт(для курсовой)', url='https://lms.hse.ru')
        l3 = types.InlineKeyboardButton('соп', url='https://www.hse.ru/evaluation/')
        markup.row(l1, l3)
        markup.row(l2)
        bot.send_message(call.message.chat.id, 'выбери нужный тебе сайт\n'
                                              '\n'
                                              '\n для возврата в главное меню нажми /start', reply_markup=markup)
    elif call.data == 'nakop':
        n1 = types.InlineKeyboardButton('мпр оценка', callback_data = 'mpr gr')
        n2 = types.InlineKeyboardButton('эсс оценка', callback_data = 'ess gr')
        n3 = types.InlineKeyboardButton('упр закуп оценка',callback_data = 'zak gr')
        n4 = types.InlineKeyboardButton('инновац деят оценка',callback_data = 'inn gr')
        n5 = types.InlineKeyboardButton('упр фин оценка', callback_data='fin gr')
        markup.row(n1)
        markup.row(n2)
        markup.row(n3)
        markup.row(n4)
        markup.row(n5)
        bot.send_message(call.message.chat.id, 'выбери предмет, в котором будем считать накоп и оценку\nдля возврата в главное меню /start', reply_markup=markup)
    elif call.data == 'mpr gr':
        mes = bot.send_message(call.message.chat.id,
                               'напиши ФИО как в ведомости (например Иванов Иван) - с большой буквы имя фамилия')
        bot.register_next_step_handler(mes,find_student)
    elif call.data in ['ess gr', 'zak gr', 'inn gr', 'fin gr']:
        names, A = formulas[call.data]
        user_data[call.message.chat.id] = {'subject': call.data,
                                           'known': [None] * (len(names) - 1)}
        k1 = types.InlineKeyboardButton('да', callback_data='known_yes')
        k2 = types.InlineKeyboardButton('нет', callback_data='known_no')
        markup.row(k1, k2)
        bot.send_message(call.message.chat.id, 'ты уже знаешь балл по какому-то элементу из формулы оценки?',
                         reply_markup=markup)
    elif call.data == 'known_yes':
        data = user_data.get(call.message.chat.id)
        if data is None:
            bot.send_message(call.message.chat.id, 'начни заново через /start')
            return
        names, A = formulas[data['subject']]
        for i in range(len(names) - 1):
            if data['known'][i] is None:
                btn = types.InlineKeyboardButton(names[i], callback_data=f'el_{i}')
                markup.row(btn)
        bot.send_message(call.message.chat.id, 'по какому элементу ты знаешь оценку?', reply_markup=markup)
    elif call.data.startswith('el_'):
        i = int(call.data[3:])
        mes = bot.send_message(call.message.chat.id, 'напиши оценку по нему (от 0 до 10)')
        bot.register_next_step_handler(mes, save_grade, i)
    elif call.data == 'known_no':
        data = user_data.get(call.message.chat.id)
        if data is None:
            bot.send_message(call.message.chat.id, 'возвращайся в главное меню /start')
            return
        mes = bot.send_message(call.message.chat.id,
                               'какую итоговую оценку хочешь? напиши ТОЛЬКО цифру (от 3.51 до 10)\n'
                               '\n'
                               '\n(если тебе например нужна 9, то пиши 8.5)')
        bot.register_next_step_handler(mes, ocenka, data['subject'])


def save_grade(message, i):
    text = message.text.replace(',', '.')
    try:
        grade = Rational(text)
    except Exception:
        bot.send_message(message.chat.id, 'нужно число, начни заново /start')
        return
    if grade < 0 or grade > 10:
        bot.send_message(message.chat.id, 'оценка должна быть от 0 до 10, начни заново /start')
        return
    data = user_data.get(message.chat.id)
    if data is None:
        bot.send_message(message.chat.id, 'начни заново: /start')
        return
    data['known'][i] = grade
    names, A = formulas[data['subject']]
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton('да', callback_data='known_yes'),
               types.InlineKeyboardButton('нет', callback_data='known_no'))
    bot.send_message(message.chat.id, f'записали: {names[i]} = {float(grade):.2f}\n'
                                      '\nзнаешь ещё какую-то оценку?', reply_markup=markup)





def find_student(message):
    fio = message.text.strip().lower()
    sheets = pd.read_excel(sheet_mpr_url, sheet_name=None, header=None)
    for group in ['241','242','243','244','245','246']:
        table = sheets[group]
        for i in range(len(table)):
            full_name = str(table.iloc[i,1])
            if fio in full_name.lower():
                hw = [x for x in table.iloc[i,2:11] if not pd.isna(x)]
                hw_1sem = Rational(str(round(sum(hw)/ len(hw),2))) if hw else None
                test1 = table.iloc[i,11]
                test2 = table.iloc[i,12]
                test_1 = None if pd.isna(test1) else Rational(str(test1))
                test_2 = None if pd.isna(test2) else Rational(str(test2))
                known = [hw_1sem, None, test_1, test_2]
                pokaz = lambda x: 'еще ничего нет' if x is None else f'{float(x):.2f}'

                mes = bot.send_message(message.chat.id,
                                           f'{full_name}, группа {group}\n'
                                           f'вот какие у тебя щас результаты\n'
                                           '\n'
                                           f'дз {pokaz(hw_1sem)}\n'
                                           f'тест 1 (октябрь){pokaz(test_1)}\n'
                                           f'тест 2 (зимой){pokaz(test_2)}\n'
                                           f'какую оценку ты хочешь получить итоговой за курс? напиши ТОЛЬКО цифру'
                                           f'\n'
                                           f'\n( напиши не результирующую оценку а тот балл который тебе нужен\nнапример хочешь получить 9 = пиши 8.5)')
                bot.register_next_step_handler(mes,ocenka_mpr,known)
                return
    bot.send_message(message.chat.id,'нет такого имени в ведомости')
def ocenka_mpr(message,known):
    text = message.text.replace(',', '.')
    try:
        oc = Rational(text)
    except Exception:
        bot.send_message(message.chat.id,'напиши число\n'
                                         '\n для возвращения в меню нажми /start')
        return
    if oc < Rational('3.51') or oc > 10:
        bot.send_message(message.chat.id,'напиши нормальную цифру в пределах от 3,51 до 10')
        return

    names = ['дз 1 сем','дз 2 сем', 'тест 1', 'тест 2', 'экз']
    A = Matrix([S(5)/100, S(5)/100, S(2)/10, S(2)/10, S(1)/2])
    e = Symbol('e')

    now = sum(A[i] * known[i] for i in range(4) if known [i] is not None)
    otvet = (f'сейчас у тебя {float(now):.2f}\n'
             f'\n тебе надо {float(oc)}\n')
    variants = [('чтобы везде был примерно одинаковый балл',oc), ('чтобы экзамен не был важен',oc+2),('готовишься к экз',oc-2)]
    for name, ball in variants:
        ball = min(max(ball,Rational('3.51')),10)
        g_1 = [k if k is not None else ball for k in known]
        g = Matrix(g_1).col_join(Matrix([e]))
        exam = solve(Eq(A.dot(g), oc), e)[0]
        if 0 <= exam <= 10:
            otvet += f'\n{name}:'
            for i in range(4):
                metka = '(уже есть)' if known[i] is not None else '(нужно)'
                otvet += f'\n  {names[i]}: {float(g[i]):.2f} {metka}'
            otvet += f'\n  экзамен: {float(exam):.2f} (нужно)\n'
    if 'экзамен:' not in otvet:
        otvet += '\n эту оценку ты не получишь даже с 10 за экз \n'

    with open ('images/mpr_formula.png', 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption = otvet + '\nдля возврата на главное меню нажми /start')



def ocenka(message, subject):
    text = message.text.replace(',', '.')
    try:
        oc = Rational(text)
    except Exception:
        bot.send_message(message.chat.id, 'напиши одно число, русским языком тебе сказали\n'
                                          '\n юзани /start и обратно в накоп')
        return
    if oc < Rational('3.51') or oc > 10:
        bot.send_message(message.chat.id, 'ты приколист я смотрю, напиши цифру от 3.51 до 10\nдля возврата в главное меню /start')
        return

    names, A = formulas[subject]
    known = user_data.get(message.chat.id, {}).get('known', [None] * (len(names) - 1))
    e = Symbol('e')
    n = A.shape[0]

    now = sum(A[i] * known[i] for i in range(n - 1) if known[i] is not None)
    otvet = f'сейчас у тебя {float(now):.2f}\nтебе надо {float(oc)}\n'
    variants = [('по каждому элементу примерно одинаково', oc),
                ('надеемся без экзамена пройти', oc + 2),
                ('готовимся на экз', oc - 2)]
    found = False
    for name, ball in variants:
        ball = min(max(ball, Rational('3.51')), 10)
        g_1 = [k if k is not None else ball for k in known]
        g = Matrix(g_1).col_join(Matrix([e]))
        exam = solve(Eq(A.dot(g), oc), e)[0]
        if 0 <= exam <= 10:
            found = True
            otvet += f'\n{name}:'
            for i in range(n - 1):
                metka = '(уже есть)' if known[i] is not None else '(нужно)'
                otvet += f'\n  {names[i]}: {float(g[i]):.2f} {metka}'
            otvet += f'\n  {names[-1]}: {float(exam):.2f} (нужно)\n'
    if not found:
        otvet += '\nэту оценку не получится набрать даже с 10 за экзамен\n'

    with open(pics[subject], 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption=otvet + '\nдля возврата в главное меню /start')


@bot.message_handler(commands=['send'])
def broadcast(message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    text = message.text.replace('/send', '', 1).strip()
    ok,fail =0,0
    for uid in list(seen):
        try:
            bot.send_message(uid, text)
            ok += 1
        except Exception:
            fail += 1
        time.sleep(0.05)
    bot.send_message(message.chat.id, f'ок ={ok}, not ok{fail}')

@bot.message_handler(func=lambda m: m.text == 'главное меню')
def menu_button(message):
    welcome(message)

bot.infinity_polling()