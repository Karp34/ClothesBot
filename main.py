# перезагрузка сервера busybox reboot
import requests
import json
from clothes import clothes
from bd_wardrobe import wardrobe
from config import settings
from config import sort_rule
from config import preference

from datetime import datetime, date, time
from pytz import timezone

now = datetime.now()
import time

import discord

client = discord.Client()

city = "moscow"
zone = 'Europe/Moscow'
cur_date = datetime.strftime(datetime.now(timezone(zone)), '%Y-%m-%d %H:%M:%S')


# получаем прогноз погоды
def city_forecast():
    response = requests.get(
        "https://community-open-weather-map.p.rapidapi.com/forecast?q=" +
        city + "&units=metric&lang=ru&cnt=6",
        headers={
            "X-RapidAPI-Host": "community-open-weather-map.p.rapidapi.com",
            "X-RapidAPI-Key":
                "829a909363msh0b8c0e070645bf9p1034cajsn75d49f6d130b"
        },
    )
    return response.json()


# Функция, которая сортирует массив с вещами по порядку сверху-вниз
def sort_clothes(not_sorted_list):
    sorted_clothes_choice = list()
    for sort_rule_k, sort_rule_v in sort_rule.items():
        for smart_obj in not_sorted_list:
            for wardrobe_item_k, wardrobe_item_v in wardrobe.items():
                if smart_obj == wardrobe_item_k and sort_rule_k == wardrobe_item_v['cl_type']:
                    sorted_clothes_choice.append(smart_obj)
    return (sorted_clothes_choice)


# В зависимости от температуры выбираем категорию одежды
def tempco(temp0):
    if temp0 <= -20:  # super_cold
        clothes_type = clothes['super_cold']
    if temp0 <= -5 and temp0 > -20:  # cold
        clothes_type = clothes['cold']
    if temp0 <= 5 and temp0 > -5:  # coldy
        clothes_type = clothes['coldy']
    if temp0 <= 15 and temp0 > 5:  # regular
        clothes_type = clothes['regular']
    if temp0 <= 20 and temp0 > 15:  # warm
        clothes_type = clothes['warm']
    if temp0 > 20:  # hot
        clothes_type = clothes['hot']
    return clothes_type


# Функция логирования событий
def log(str_obj):
    with open("logs.txt", 'a+') as f:
        zone = 'Europe/Moscow'
        cur_date = datetime.strftime(datetime.now(timezone(zone)),
                                     '%Y-%m-%d %H:%M:%S')
        f.write("\n")
        new_line = cur_date + " - " + str_obj
        f.write(new_line)
        f.close()


# Функция проверки наличия вещей в гардеробе и добавления, если нет
def add_clothes(new_cloth):
    if new_cloth in wardrobe.keys():
        print("Уже в гардеробе")
    else:
        wardrobe[new_cloth] = dict()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    msg = message.content
    log(msg)
    timelist = list()
    if message.author == client.user:
        return

    def weather_orient(clothes_type):
        right_clothes = dict()
        # В зависимости от прогноза выбираем тип одежды, если в нексколько в списке: 1 - солнце, 2 - дождь, гроза, пасмурно, сильный ветер, 3 - высокая влажность и не 2, 4 - пасмурно
        for k, v in clothes_type.items():
            if v is False: continue
            if int(str(abs(weather_id))[0]) == 2 or int(str(abs(weather_id))[0]) == 6 or int(
                    str(abs(weather_id))[0]) == 5 or wind_speed > 15:
                if type(v) is list:
                    value = v[1]
                else:
                    value = v
                if value is False: continue
                right_clothes[k] = value
            elif humidity > 65:  # Влажность
                if type(v) is list and len(v) < 3:
                    value = v[0]
                elif type(v) is list and len(v) >= 3:
                    value = v[2]
                else:
                    value = v
                if value is False: continue
                right_clothes[k] = value
            elif weather_id == 804:  # Пасмурно
                if type(v) is list and len(v) < 4:
                    value = v[0]
                elif type(v) is list and len(v) >= 4:
                    value = v[3]
                else:
                    value = v
                if value is False: continue
                right_clothes[k] = value
            else:
                if type(v) is list:
                    value = v[0]
                else:
                    value = v
                if value is False: continue
                right_clothes[k] = value
        return right_clothes

    if message.content.startswith('!start'):
        from bd_wardrobe import wardrobe
        # Вводим переменную n и делаем loop, чтобы при некоторых обстоятельствах можно было его остановить.
        n = 0
        while n != 1:
            if wardrobe == {}:
                await message.channel.send("Нет вещей в гардеробе")
                break
            weather_dict = {}
            weather_dict[city] = city_forecast()
            weather_json = city_forecast()
            weather_json_list = weather_json['list']
            # pred_json_list = weather_json_list['dt_txt']
            text_json = str(weather_json['list'])
            log("\n")
            log(text_json)

            line_count = 0
            for line in weather_json_list:
                line_count = line_count + 1
                print(line_count)
                if line_count > 8: break
                date_time_str = line['dt_txt']
                cur_date = datetime.strftime(datetime.now(timezone(zone)), '%Y-%m-%d %H:%M:%S')
                date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
                date_time_obj2 = datetime.strptime(cur_date, '%Y-%m-%d %H:%M:%S')
                time_dif = date_time_obj2 - date_time_obj
                minutes = time_dif.total_seconds() // 60
                if minutes > 90:
                    print("skip")
                    print("minutes:", minutes)
                    continue
                temp_txt = line['main']['temp_min']
                if temp_txt < 0:
                    module_temp = ", -" + str(round(temp_txt))
                elif temp_txt == 0:
                    module_temp = ", " + str(round(temp_txt))
                else:
                    module_temp = ", +" + str(round(temp_txt))
                time_txt = line['dt_txt']
                weather_id = line['weather'][0]['id']
                weather_type = line['weather'][0]['description']

                prefer_temp = temp_txt + preference
                clothes_type = tempco(prefer_temp)
                humidity = line['main']['humidity']
                wind_speed = line['wind']['speed']
                right_choice = weather_orient(clothes_type)
                print(temp_txt)
                print(right_choice)
                log(str(right_choice))
                timelist.append(str(time_txt) + ", " + str(weather_type) + str(module_temp))
                items = right_choice.items()
                all_fits = list()

                for x in range(20):
                    clothes_choice = list()
                    full_clothes_choice = list()
                    for k, v in items:
                        clo_type = k
                        clo_temp = v
                        for w_key, w_val in wardrobe.items():
                            if clo_type == w_val['cl_type'] and clo_temp == w_val['temp'] and x in w_val['fit_id']:
                                # print(w_key)
                                exist_types = list()
                                if len(full_clothes_choice) > 0:
                                    for clothes_choice_item in full_clothes_choice:
                                        for clothes_choice_item_k, clothes_choice_item_v in clothes_choice_item.items():
                                            exist_type = clothes_choice_item_v["cl_type"]
                                            exist_types.append(exist_type)
                                if w_key not in full_clothes_choice and w_val["cl_type"] not in exist_types:
                                    clodict = dict()
                                    clodict[w_key] = w_val
                                    full_clothes_choice.append(clodict)
                                if w_val["cl_type"] not in exist_types and w_key not in clothes_choice:
                                    clothes_choice.append(w_key)
                                '''
                                print("clothes_choice:", clothes_choice)
                                print("full_clothes_choice:", full_clothes_choice)
                                print("exist_types:", exist_types)
                                print("   ")
                                '''

                    if len(clothes_choice) == len(right_choice):
                        # print(clothes_choice)
                        sorted_clothes_choice = sort_clothes(clothes_choice)
                        sorted_clothes_choice.append(" ")
                        outfit = "\n".join(sorted_clothes_choice)
                        all_fits.append(outfit)
                        # print(all_fits)

                # print("if starts")
                if len(all_fits) > 0:
                    print("if")
                    print(all_fits)
                    all_fits_str = "\n".join(all_fits)
                    timelist.append(all_fits_str)
                    timelist.append(" ")
                else:
                    print("else")
                    for x in range(15):
                        clothes_choice = list()
                        for k, v in items:
                            if v is False: continue
                            clo_type = k
                            clo_temp = v
                            for w_key, w_val in wardrobe.items():
                                if clo_type == w_val['cl_type'] and clo_temp == w_val['temp']:
                                    if w_key not in clothes_choice:
                                        clodict = dict()
                                        clodict[w_key] = w_val
                                        clothes_choice.append(clodict)

                        # собирает комлект из вещей, которые подходят по погоде и сочетаются хотябы с одной вещью из подходящих по погоде

                        for item_clothes_choice in clothes_choice:
                            for clodict_k, clodict_v in item_clothes_choice.items():
                                clodict_k_fitid = clodict_v['fit_id']
                                smart_fit = list()
                                for item_cloth in clothes_choice:
                                    for clo_k, clo_v in item_cloth.items():
                                        clo_k_fitid = clo_v['fit_id']
                                        if clodict_k == clo_k:
                                            continue
                                        else:
                                            dif_clodict_fit = list(set(clodict_k_fitid) & set(clo_k_fitid))
                                            exist_types = list()
                                            if len(smart_fit) > 0:
                                                for smart_item in smart_fit:
                                                    for smart_item_k, smart_item_v in smart_item.items():
                                                        exist_type = smart_item_v["cl_type"]
                                                        exist_types.append(exist_type)

                                            if len(dif_clodict_fit) > 0 and clodict_k not in smart_fit and clodict_v[
                                                "cl_type"] not in exist_types:
                                                smart_fit.append(item_clothes_choice)
                                            if len(dif_clodict_fit) > 0 and clo_k not in smart_fit and clo_v[
                                                "cl_type"] not in exist_types:
                                                smart_fit.append(item_cloth)

                                smart_fit_list = list()

                                for x_item in smart_fit:
                                    for k, v in x_item.items():
                                        smart_fit_list.append(k)

                                if len(smart_fit_list) == len(right_choice):
                                    sorted_smart_fit_list = sort_clothes(smart_fit_list)

                                    if len(all_fits) > 0:
                                        count_fits = 0
                                        sum_difs = 0
                                        for item_fit_list in all_fits:
                                            count_fits = count_fits + 1
                                            dif_smart_lists = list(set(item_fit_list) - set(sorted_smart_fit_list))
                                            if len(dif_smart_lists) > 0:
                                                sum_difs = sum_difs + 1
                                        if len(dif_smart_lists) == count_fits:
                                            all_fits.append(sorted_smart_fit_list)
                                    else:
                                        all_fits.append(sorted_smart_fit_list)
                    '''
                    for str_all_fit in all_fits:
                      str_all_fit.append(" ")
                    str_all_fits = "\n".join(str_all_fit)
                    '''

                    if len(all_fits) == 1:
                        timelist.append(
                            "Нет комплекта для такой погоды. Показываю комплект, сгенерированный по предпочтениям"
                        )
                    elif len(all_fits) > 1:
                        timelist.append(
                            "Нет комплектов для такой погоды. Показываю комплекты, сгенерированные по предпочтениям")
                    elif len(all_fits) == 0:
                        timelist.append("В твоем гардеробе не хватает вещей")
                    for all_fit_item in all_fits:
                        all_fit_item.append(" ")
                        str_all_fit = "\n".join(all_fit_item)
                        timelist.append(str_all_fit)
                        # timelist.append(" ")
            n = 1

            output = "\n".join(timelist)
            await message.channel.send(output)

    if message.content.startswith('!type'):
        from bd_wardrobe import wardrobe
        all_types = list()
        for k, v in wardrobe.items():
            try:
                clothes_type = v["cl_type"]
                if clothes_type not in all_types:
                    all_types.append(clothes_type)
            except:
                continue
        mes = "Доступные типы: \n" + str(all_types).strip("[]")
        await message.channel.send(mes)

    if message.content.startswith('!help'):
        from bd_wardrobe import wardrobe
        orig_wardrobe = str(wardrobe)
        help_info = 'Чтобы увидеть лук по погоде, введи !start. \nЧтобы увидеть лук на весь день, введи !allday \nЧтобы увидеть лук на всю ночь, введи !allnight \nЧтобы добавить вещь, введи через запятую: !new, Название вещи, Тип, Тип погоды, Цвет, например "!new, Синяя кофта, sweater, coldy, blue" \nЧтобы удалить вещь из гардероба, введи !delname: *название вещи*, например: "!delname: Синяя куртка"\nЧтобы посмотреть типы вещей из гардероба, введи !type\nЧтобы посмотреть комплект по номеру id, введи: !fit *номер id*, например "!fit 2"\nЧтобы добавить новый комплект введи: !addfit: и названия вещей через запятую, например: !addfit: Красная кофта, Черная футболка, Черные штаны, Высокие носки, Найки\nЧтобы удалить комплект введи !delfit: и номер id комплекта, например "!delfit: 9"'
        await message.channel.send(help_info)

    if message.content.startswith('!new'):
        from bd_wardrobe import wardrobe
        orig_wardrobe = str(wardrobe)
        print(orig_wardrobe)
        new_cloth = msg
        items = new_cloth.split(',')
        new_cloth_name = items[1].strip(" ")
        new_cloth_type = items[2].strip(" ")
        new_cloth_temp = items[3].strip(" ")
        new_cloth_color = items[4].strip(" ")
        # new_cloth_fit = items[5].strip(" ")

        num = 0
        while num != 1:
            if new_cloth_name in wardrobe.keys():
                await message.channel.send("Уже в гардеробе. Поменяй название")
                break

            all_types = list()
            for k, v in wardrobe.items():
                try:
                    clothes_type = v["cl_type"]
                    if clothes_type not in all_types:
                        all_types.append(clothes_type)
                except:
                    continue

            if len(all_types) > 0 and new_cloth_type not in all_types:
                mes = "Нет введенного типа. Доступные типы:\n" + str(
                    all_types).strip("[]")
                await message.channel.send(mes)
                break

            all_temps = list()
            for k, v in clothes.items():
                try:
                    clothes_temp = k
                    if clothes_temp not in all_temps:
                        all_temps.append(clothes_temp)
                except:
                    continue

            if len(all_temps) > 0 and new_cloth_temp not in all_temps:
                await message.channel.send("Нет введенного типа погоды")
                break

            all_colors = list()
            if new_cloth_color.startswith("$") is False:
                for k, v in wardrobe.items():
                    try:
                        color = v["color"]
                        if color not in all_colors:
                            all_colors.append(color)
                    except:
                        continue

                if len(all_colors) >= 0 and new_cloth_color not in all_colors:
                    await message.channel.send(
                        "Нет введенного цвета (введи $ перед цветом, чтобы добавить новый цвет"
                    )
                    break

            wardrobe[new_cloth_name] = 0
            wardrobe[new_cloth_name] = {"cl_type": new_cloth_type}
            wardrobe[new_cloth_name]["temp"] = new_cloth_temp
            wardrobe[new_cloth_name]["color"] = new_cloth_color
            wardrobe[new_cloth_name]["fit_id"] = []

            with open("bd_wardrobe.py", 'w') as f:
                str_wardrobe = json.dumps(wardrobe,
                                          indent=4,
                                          ensure_ascii=False)
                new_item = "wardrobe = " + str_wardrobe
                f.write(new_item)
                f.close()

            num = 1
            await message.channel.send("Ok")

    if message.content.startswith('!fit'):
        from bd_wardrobe import wardrobe
        m = 0
        while m != 1:
            fit_info = msg
            items = fit_info.split()
            if len(items) < 2:
                await message.channel.send("Не введен fit id")
                break
            info_id = int(items[1])
            fit_list = list()

            for k, v in wardrobe.items():
                try:
                    fit = v["fit_id"]
                    for obj in fit:
                        if info_id == obj:
                            fit_line = k + ", id: " + str(info_id)
                            fit_list.append(fit_line)
                            fit_output = "\n".join(fit_list)
                except:
                    continue

            if len(fit_list) < 1:
                fit_output = "Ошибка, по этому fit id ничего не найдено"
            await message.channel.send(fit_output)
            m = 1

    if message.content.startswith('!delname'):
        from bd_wardrobe import wardrobe
        with open('bd_wardrobe.py') as f:
            data = f.read()
            d = data[10:]
            old_wardrobe = json.loads(d)
        del_item = msg
        items = del_item.split(":")
        item_name = items[1].strip()
        wardrobe.pop(item_name, None)
        with open("bd_wardrobe.py", 'w') as f:
            str_wardrobe = json.dumps(wardrobe, indent=4, ensure_ascii=False)
            new_item = "wardrobe = " + str_wardrobe
            f.write(new_item)
            f.close()
        from bd_wardrobe import wardrobe
        if item_name not in wardrobe and item_name not in old_wardrobe:
            await message.channel.send("Нет в гардеробе")
        if item_name not in wardrobe and item_name in old_wardrobe:
            await message.channel.send("Ok")

    if message.content.startswith('!addfit'):
        from bd_wardrobe import wardrobe
        items = message.content.split(":")
        biggest_id = 0
        for k, v in wardrobe.items():
            for ids in v['fit_id']:
                if ids > biggest_id:
                    biggest_id = ids
        new_fit_id = biggest_id + 1
        print(new_fit_id)
        fit_clothes = items[1]
        fit_clo_list = fit_clothes.split(",")
        print(fit_clo_list)

        count_item = 0
        for item in fit_clo_list:
            item = item.strip()
            if item not in wardrobe:
                mess = "Не удалось найти " + str(
                    item
                ) + " в гардеробе. Измени название или добавь в гардероб"
                await message.channel.send(mess)
                break
            count_item = count_item + 1

        first_item = fit_clo_list[0].strip()
        result = wardrobe[first_item]["fit_id"]
        if count_item == len(fit_clo_list):
            for item in fit_clo_list:
                item = item.strip()
                new_fits = wardrobe[item]["fit_id"]
                result = list(set(new_fits) & set(result))

        if len(result) == 0:
            for item in fit_clo_list:
                item = item.strip()
                new_fits = wardrobe[item]["fit_id"]
                new_fits.append(new_fit_id)
                wardrobe[item]["fit_id"] = new_fits

            with open("bd_wardrobe.py", 'w') as f:
                str_wardrobe = json.dumps(wardrobe,
                                          indent=4,
                                          ensure_ascii=False)
                new_item = "wardrobe = " + str_wardrobe
                f.write(new_item)
                f.close()
            await message.channel.send("Новый лук добавлен в гардероб")

        if len(result) > 0 and result != wardrobe[first_item]["fit_id"]:
            mes = "Такой лук уже есть в гардеробе под номером: " + str(
                result).strip("[]")
            await message.channel.send(mes)

    if message.content.startswith('!delfit'):
        from bd_wardrobe import wardrobe

        del_item = msg
        items = del_item.split(":")
        item_fit = int(items[1].strip())
        print(item_fit)
        for k, v in wardrobe.items():
            fit_id_list = v["fit_id"]
            if item_fit in fit_id_list:
                fit_id_list.remove(item_fit)
        fit_id_am = 0
        for k, v in wardrobe.items():
            fit_id_list = v["fit_id"]
            if item_fit in fit_id_list:
                fit_id_am = fit_id_am + 1
        if fit_id_am == 0:
            mes = "Ok"
            await message.channel.send(mes)

    if message.content.startswith('!allnight'):
        from bd_wardrobe import wardrobe
        # Вводим переменную n и делаем loop, чтобы при некоторых обстоятельствах можно было его остановить.
        n = 0
        while n != 1:
            if wardrobe == {}:
                await message.channel.send("Нет вещей в гардеробе")
                break
            weather_dict = {}
            weather_dict[city] = city_forecast()
            weather_json = city_forecast()
            weather_json_list = weather_json['list']
            # pred_json_list = weather_json_list['dt_txt']
            text_json = str(weather_json['list'])
            log("\n")
            log(text_json)

            right_fit_list = list()
            for line in weather_json_list:
                line_date = line['dt_txt'].split()
                line_time = line_date[1].split(":")
                line_hour = line_time[0]
                if int(line_hour) > 8: continue

                weather_id = line['weather'][0]['id']
                humidity = line['main']['humidity']
                wind_speed = line['wind']['speed']
                temp_txt = line['main']['temp_min']
                prefer_temp = temp_txt + preference
                clothes_type = tempco(prefer_temp)
                right_choice = weather_orient(clothes_type)
                right_fit_list.append(right_choice)

            right_choice = dict()
            for sort_rule_k, sort_rule_v in sort_rule.items():
                right_dict_v_list = list()
                for right_dict in right_fit_list:
                    for right_dict_k, right_dict_v in right_dict.items():
                        if sort_rule_k == right_dict_k:
                            right_dict_v_list.append(right_dict_v)
                sort_rule_k_str = sort_rule_k + ": " + str(right_dict_v_list)
                print(sort_rule_k_str)
                log(sort_rule_k_str)

                from collections import Counter
                right_cloth_dict = dict(Counter(right_dict_v_list))
                sortedrcd = sorted(right_cloth_dict.items(),
                                   key=lambda x: x[1],
                                   reverse=True)
                the_biggest_item = None
                the_biggest_count = 0
                the_biggest_list = list()
                print(sortedrcd)
                for item in sortedrcd:
                    print(the_biggest_item, the_biggest_count)
                    if the_biggest_item == None:
                        the_biggest_item = item[0]
                        the_biggest_count = item[1]
                    elif the_biggest_count < item[1]:
                        the_biggest_item = item[0]
                        the_biggest_count = item[1]
                        the_biggest_list = []
                    elif the_biggest_count == item[1]:
                        if item[0] not in the_biggest_list:
                            print("item[0]")
                            the_biggest_list.append(item[0])
                        if the_biggest_item not in the_biggest_list:
                            print("the_biggest_item", the_biggest_item)
                            the_biggest_list.append(the_biggest_item)
                    print(the_biggest_list)
                    print(" ")

                if the_biggest_list == [] and the_biggest_item != None:
                    right_choice[sort_rule_k] = the_biggest_item
                else:
                    from config import temps
                    if preference < 0:
                        for temper in temps:
                            if temper in the_biggest_list:
                                right_choice[sort_rule_k] = temper
                                break

                    elif preference == 0 and len(the_biggest_list) >= 3:
                        sorted_list = list()
                        for temper in temps:
                            if temper in the_biggest_list:
                                sorted_list.append(temper)
                        right_choice[sort_rule_k] = sorted_list[1]

                    elif preference >= 0:
                        reverse_temps = sorted(temps, reverse=True)
                        for temper in reverse_temps:
                            if temper in the_biggest_list:
                                right_choice[sort_rule_k] = temper
                                break

            temp_txt = line['main']['temp_min']
            if temp_txt < 0:
                module_temp = ", -" + str(round(temp_txt))
            elif temp_txt == 0:
                module_temp = ", " + str(round(temp_txt))
            else:
                module_temp = ", +" + str(round(temp_txt))
            time_txt = line['dt_txt']
            only_date = time_txt.split()[0]
            weather_id = line['weather'][0]['id']
            weather_type = line['weather'][0]['description']
            # print("right_choice - ", right_choice)
            log(str(right_choice))
            # timelist.append("Комплект на весь день")

            items = right_choice.items()
            print(items)
            # проверяем подходит ли вся одежда в комплектах для данной погоды
            all_fits = list()

            for x in range(20):
                # print(x)
                clothes_choice = list()
                full_clothes_choice = list()
                for k, v in items:
                    if v is False: continue
                    clo_type = k
                    clo_temp = v

                    for w_key, w_val in wardrobe.items():
                        if clo_type == w_val['cl_type'] and clo_temp == w_val['temp'] and x in w_val['fit_id']:
                            exist_types = list()
                            # print(w_key)
                            if len(full_clothes_choice) > 0:
                                for clothes_choice_item in full_clothes_choice:
                                    for clothes_choice_item_k, clothes_choice_item_v in clothes_choice_item.items(
                                    ):
                                        exist_type = clothes_choice_item_v["cl_type"]
                                        exist_types.append(exist_type)
                            if w_key not in full_clothes_choice and w_val["cl_type"] not in exist_types:
                                clodict = dict()
                                clodict[w_key] = w_val
                                full_clothes_choice.append(clodict)

                            if w_val["cl_type"] not in exist_types and w_key not in clothes_choice:
                                clothes_choice.append(w_key)

                    # print("clothes_choice", len(clothes_choice), clothes_choice)
                    # print("right_choice", len(right_choice), right_choice)
                    if len(clothes_choice) == len(right_choice):
                        sorted_clothes_choice = sort_clothes(clothes_choice)
                        sorted_clothes_choice.append(" ")
                        outfit = "\n".join(sorted_clothes_choice)
                        # print("outfit", outfit)
                        all_fits.append(outfit)
                # print("   ")
                # print("   ")

            if len(all_fits) > 0:
                all_fits_str = "\n".join(all_fits)
                heading = only_date + ", комплект на весь день"
                timelist.append(heading)
                timelist.append(all_fits_str)
                timelist.append(" ")
            else:
                for x in range(15):
                    clothes_choice = list()
                    for k, v in items:
                        if v is False: continue
                        clo_type = k
                        clo_temp = v
                        for w_key, w_val in wardrobe.items():
                            if clo_type == w_val[
                                'cl_type'] and clo_temp == w_val['temp']:
                                if w_key not in clothes_choice:
                                    clodict = dict()
                                    clodict[w_key] = w_val
                                    clothes_choice.append(clodict)

                # собирает комлект из вещей, которые подходят по погоде и сочетаются хотябы с одной вещью из подходящих по погоде

                for item_clothes_choice in clothes_choice:
                    for clodict_k, clodict_v in item_clothes_choice.items():
                        clodict_k_fitid = clodict_v['fit_id']
                        smart_fit = list()
                        for item_cloth in clothes_choice:
                            for clo_k, clo_v in item_cloth.items():
                                clo_k_fitid = clo_v['fit_id']
                                if clodict_k == clo_k:
                                    continue
                                else:
                                    dif_clodict_fit = list(set(clodict_k_fitid) & set(clo_k_fitid))
                                    exist_types = list()
                                    if len(smart_fit) > 0:
                                        for smart_item in smart_fit:
                                            for smart_item_k, smart_item_v in smart_item.items():
                                                exist_type = smart_item_v["cl_type"]
                                                exist_types.append(exist_type)

                                    if len(dif_clodict_fit) > 0 and clodict_k not in smart_fit and clodict_v[
                                        "cl_type"] not in exist_types:
                                        smart_fit.append(item_clothes_choice)
                                    if len(dif_clodict_fit) > 0 and clo_k not in smart_fit and clo_v[
                                        "cl_type"] not in exist_types:
                                        smart_fit.append(item_cloth)

                        smart_fit_list = list()

                        for x_item in smart_fit:
                            for k, v in x_item.items():
                                smart_fit_list.append(k)

                        if len(smart_fit_list) == len(right_choice):
                            sorted_smart_fit_list = sort_clothes(smart_fit_list)

                            if len(all_fits) > 0:
                                count_fits = 0
                                sum_difs = 0
                                for item_fit_list in all_fits:
                                    count_fits = count_fits + 1
                                    dif_smart_lists = list(set(item_fit_list) - set(sorted_smart_fit_list))
                                    if len(dif_smart_lists) > 0:
                                        sum_difs = sum_difs + 1
                                if len(dif_smart_lists) == count_fits:
                                    all_fits.append(sorted_smart_fit_list)
                            else:
                                all_fits.append(sorted_smart_fit_list)

                # print("all_fits", all_fits)
                '''
                for str_all_fit in all_fits:
                  str_all_fit.append(" ")
                str_all_fits = "\n".join(str_all_fit)
                '''

                if len(all_fits) == 1:
                    timelist.append(
                        "Нет комплекта для такой погоды. Показываю комплект, сгенерированный по предпочтениям"
                    )
                elif len(all_fits) > 1:
                    timelist.append(
                        "Нет комплектов для такой погоды. Показываю комплекты, сгенерированные по предпочтениям"
                    )
                for all_fit_item in all_fits:
                    all_fit_item.append(" ")
                    str_all_fit = "\n".join(all_fit_item)
                    timelist.append(str_all_fit)
            n = 1
            output = "\n".join(timelist)
            await message.channel.send(output)
            # начало

    if message.content.startswith('!allday'):
        from bd_wardrobe import wardrobe
        # Вводим переменную n и делаем loop, чтобы при некоторых обстоятельствах можно было его остановить.
        n = 0
        while n != 1:
            if wardrobe == {}:
                await message.channel.send("Нет вещей в гардеробе")
                break
            weather_dict = {}
            weather_dict[city] = city_forecast()
            weather_json = city_forecast()
            weather_json_list = weather_json['list']
            # pred_json_list = weather_json_list['dt_txt']
            text_json = str(weather_json['list'])
            log("\n")
            log(text_json)

            right_fit_list = list()
            for line in weather_json_list:
                line_date = line['dt_txt'].split()
                line_time = line_date[1].split(":")
                line_hour = line_time[0]
                if int(line_hour) < 8: continue

                weather_id = line['weather'][0]['id']
                humidity = line['main']['humidity']
                wind_speed = line['wind']['speed']
                temp_txt = line['main']['temp_min']
                prefer_temp = temp_txt + preference
                clothes_type = tempco(prefer_temp)
                right_choice = weather_orient(clothes_type)
                right_fit_list.append(right_choice)

            right_choice = dict()
            for sort_rule_k, sort_rule_v in sort_rule.items():
                right_dict_v_list = list()
                for right_dict in right_fit_list:
                    for right_dict_k, right_dict_v in right_dict.items():
                        if sort_rule_k == right_dict_k:
                            right_dict_v_list.append(right_dict_v)
                sort_rule_k_str = sort_rule_k + ": " + str(right_dict_v_list)
                print(sort_rule_k_str)
                log(sort_rule_k_str)

                from collections import Counter
                right_cloth_dict = dict(Counter(right_dict_v_list))
                sortedrcd = sorted(right_cloth_dict.items(),
                                   key=lambda x: x[1],
                                   reverse=True)
                the_biggest_item = None
                the_biggest_count = 0
                the_biggest_list = list()
                for item in sortedrcd:
                    if the_biggest_item == None:
                        the_biggest_item = item[0]
                        the_biggest_count = item[1]
                    elif the_biggest_count < item[1]:
                        the_biggest_item = item[0]
                        the_biggest_count = item[1]
                        the_biggest_list = []
                    elif the_biggest_count == item[1]:
                        if item not in the_biggest_list:
                            the_biggest_list.append(item)
                        if the_biggest_item not in the_biggest_list:
                            the_biggest_list.append(the_biggest_item)

                if the_biggest_list == [] and the_biggest_item != None:
                    right_choice[sort_rule_k] = the_biggest_item
                else:
                    from config import temps
                    if preference < 0:
                        for temper in temps:
                            if temper in the_biggest_list:
                                right_choice[sort_rule_k] = temper
                                break

                    elif preference == 0 and len(the_biggest_list) >= 3:
                        sorted_list = list()
                        for temper in temps:
                            if temper in the_biggest_list:
                                sorted_list.append(temper)
                        right_choice[sort_rule_k] = sorted_list[1]

                    elif preference >= 0:
                        reverse_temps = sorted(temps, reverse=True)
                        for temper in reverse_temps:
                            if temper in the_biggest_list:
                                right_choice[sort_rule_k] = temper
                                break

            temp_txt = line['main']['temp_min']
            if temp_txt < 0:
                module_temp = ", -" + str(round(temp_txt))
            elif temp_txt == 0:
                module_temp = ", " + str(round(temp_txt))
            else:
                module_temp = ", +" + str(round(temp_txt))
            time_txt = line['dt_txt']
            only_date = time_txt.split()[0]
            weather_id = line['weather'][0]['id']
            weather_type = line['weather'][0]['description']
            # print("right_choice - ", right_choice)
            log(str(right_choice))
            # timelist.append("Комплект на весь день")

            items = right_choice.items()
            print(items)
            # проверяем подходит ли вся одежда в комплектах для данной погоды
            all_fits = list()
            for x in range(20):
                # print(x)
                clothes_choice = list()
                full_clothes_choice = list()
                for k, v in items:
                    if v is False: continue
                    clo_type = k
                    clo_temp = v

                    for w_key, w_val in wardrobe.items():
                        if clo_type == w_val['cl_type'] and clo_temp == w_val['temp'] and x in w_val['fit_id']:
                            exist_types = list()
                            # print(w_key)
                            if len(full_clothes_choice) > 0:
                                for clothes_choice_item in full_clothes_choice:
                                    for clothes_choice_item_k, clothes_choice_item_v in clothes_choice_item.items(
                                    ):
                                        exist_type = clothes_choice_item_v["cl_type"]
                                        exist_types.append(exist_type)
                            if w_key not in full_clothes_choice and w_val["cl_type"] not in exist_types:
                                clodict = dict()
                                clodict[w_key] = w_val
                                full_clothes_choice.append(clodict)

                            if w_val["cl_type"] not in exist_types and w_key not in clothes_choice:
                                clothes_choice.append(w_key)

                    # print("clothes_choice", len(clothes_choice), clothes_choice)
                    # print("right_choice", len(right_choice), right_choice)
                    if len(clothes_choice) == len(right_choice):
                        sorted_clothes_choice = sort_clothes(clothes_choice)
                        sorted_clothes_choice.append(" ")
                        outfit = "\n".join(sorted_clothes_choice)
                        # print("outfit", outfit)
                        all_fits.append(outfit)
                # print("   ")
                # print("   ")

            if len(all_fits) > 0:
                all_fits_str = "\n".join(all_fits)
                heading = only_date + ", комплект на весь день"
                timelist.append(heading)
                timelist.append(all_fits_str)
                timelist.append(" ")
            else:
                for x in range(15):
                    clothes_choice = list()
                    for k, v in items:
                        if v is False: continue
                        clo_type = k
                        clo_temp = v
                        for w_key, w_val in wardrobe.items():
                            if clo_type == w_val['cl_type'] and clo_temp == w_val['temp']:
                                if w_key not in clothes_choice:
                                    clodict = dict()
                                    clodict[w_key] = w_val
                                    clothes_choice.append(clodict)

                # собирает комлект из вещей, которые подходят по погоде и сочетаются хотябы с одной вещью из подходящих по погоде

                for item_clothes_choice in clothes_choice:
                    for clodict_k, clodict_v in item_clothes_choice.items():
                        clodict_k_fitid = clodict_v['fit_id']
                        smart_fit = list()
                        for item_cloth in clothes_choice:
                            for clo_k, clo_v in item_cloth.items():
                                clo_k_fitid = clo_v['fit_id']
                                if clodict_k == clo_k:
                                    continue
                                else:
                                    dif_clodict_fit = list(set(clodict_k_fitid) & set(clo_k_fitid))
                                    exist_types = list()
                                    if len(smart_fit) > 0:
                                        for smart_item in smart_fit:
                                            for smart_item_k, smart_item_v in smart_item.items():
                                                exist_type = smart_item_v["cl_type"]
                                                exist_types.append(exist_type)

                                    if len(dif_clodict_fit) > 0 and clodict_k not in smart_fit and clodict_v[
                                        "cl_type"] not in exist_types:
                                        smart_fit.append(item_clothes_choice)
                                    if len(dif_clodict_fit) > 0 and clo_k not in smart_fit and clo_v[
                                        "cl_type"] not in exist_types:
                                        smart_fit.append(item_cloth)

                        smart_fit_list = list()

                        for x_item in smart_fit:
                            for k, v in x_item.items():
                                smart_fit_list.append(k)

                        if len(smart_fit_list) == len(right_choice):
                            sorted_smart_fit_list = sort_clothes(smart_fit_list)

                            if len(all_fits) > 0:
                                count_fits = 0
                                sum_difs = 0
                                for item_fit_list in all_fits:
                                    count_fits = count_fits + 1
                                    dif_smart_lists = list(set(item_fit_list) - set(sorted_smart_fit_list))
                                    if len(dif_smart_lists) > 0:
                                        sum_difs = sum_difs + 1
                                if len(dif_smart_lists) == count_fits:
                                    all_fits.append(sorted_smart_fit_list)
                            else:
                                all_fits.append(sorted_smart_fit_list)

                # print("all_fits", all_fits)
                '''
                for str_all_fit in all_fits:
                  str_all_fit.append(" ")
                str_all_fits = "\n".join(str_all_fit)
                '''

                if len(all_fits) == 1:
                    timelist.append(
                        "Нет комплекта для такой погоды. Показываю комплект, сгенерированный по предпочтениям"
                    )
                elif len(all_fits) > 1:
                    timelist.append(
                        "Нет комплектов для такой погоды. Показываю комплекты, сгенерированные по предпочтениям"
                    )
                for all_fit_item in all_fits:
                    all_fit_item.append(" ")
                    str_all_fit = "\n".join(all_fit_item)
                    timelist.append(str_all_fit)
            n = 1
            output = "\n".join(timelist)
            await message.channel.send(output)
            # начало

    if message.content.startswith('!neday'):
        from bd_wardrobe import wardrobe
        # Вводим переменную n и делаем loop, чтобы при некоторых обстоятельствах можно было его остановить.
        n = 0
        while n != 1:
            if wardrobe == {}:
                await message.channel.send("Нет вещей в гардеробе")
                break
            weather_dict = {}
            weather_dict[city] = city_forecast()
            weather_json = city_forecast()
            weather_json_list = weather_json['list']
            # pred_json_list = weather_json_list['dt_txt']
            text_json = str(weather_json['list'])
            log("\n")
            log(text_json)

            right_fit_list = list()
            for line in weather_json_list:
                line_date = line['dt_txt'].split()
                line_time = line_date[1].split(":")
                line_hour = line_time[0]
                if int(line_hour) < 8: continue

                weather_id = line['weather'][0]['id']
                humidity = line['main']['humidity']
                wind_speed = line['wind']['speed']
                temp_txt = line['main']['temp_min']
                prefer_temp = temp_txt + preference
                clothes_type = tempco(prefer_temp)
                right_choice = weather_orient(clothes_type)
                right_fit_list.append(right_choice)

            right_choice = dict()
            for sort_rule_k, sort_rule_v in sort_rule.items():
                right_dict_v_list = list()
                for right_dict in right_fit_list:
                    for right_dict_k, right_dict_v in right_dict.items():
                        if sort_rule_k == right_dict_k:
                            right_dict_v_list.append(right_dict_v)
                sort_rule_k_str = sort_rule_k + ": " + str(right_dict_v_list)
                print(sort_rule_k_str)
                log(sort_rule_k_str)

                from collections import Counter
                right_cloth_dict = dict(Counter(right_dict_v_list))
                sortedrcd = sorted(right_cloth_dict.items(),
                                   key=lambda x: x[1],
                                   reverse=True)
                the_biggest_item = None
                the_biggest_count = 0
                the_biggest_list = list()
                for item in sortedrcd:
                    if the_biggest_item == None:
                        the_biggest_item = item[0]
                        the_biggest_count = item[1]
                    elif the_biggest_count < item[1]:
                        the_biggest_item = item[0]
                        the_biggest_count = item[1]
                        the_biggest_list = []
                    elif the_biggest_count == item[1]:
                        if item not in the_biggest_list:
                            the_biggest_list.append(item)
                        if the_biggest_item not in the_biggest_list:
                            the_biggest_list.append(the_biggest_item)

                if the_biggest_list == [] and the_biggest_item != None:
                    right_choice[sort_rule_k] = the_biggest_item
                else:
                    from config import temps
                    if preference < 0:
                        for temper in temps:
                            if temper in the_biggest_list:
                                right_choice[sort_rule_k] = temper
                                break

                    elif preference == 0 and len(the_biggest_list) >= 3:
                        sorted_list = list()
                        for temper in temps:
                            if temper in the_biggest_list:
                                sorted_list.append(temper)
                        right_choice[sort_rule_k] = sorted_list[1]

                    elif preference >= 0:
                        reverse_temps = sorted(temps, reverse=True)
                        for temper in reverse_temps:
                            if temper in the_biggest_list:
                                right_choice[sort_rule_k] = temper
                                break

            temp_txt = line['main']['temp_min']
            if temp_txt < 0:
                module_temp = ", -" + str(round(temp_txt))
            elif temp_txt == 0:
                module_temp = ", " + str(round(temp_txt))
            else:
                module_temp = ", +" + str(round(temp_txt))
            time_txt = line['dt_txt']
            only_date = time_txt.split()[0]
            weather_id = line['weather'][0]['id']
            weather_type = line['weather'][0]['description']
            # print("right_choice - ", right_choice)
            log(str(right_choice))
            # timelist.append("Комплект на весь день")
            from clothes_giver import give_clothes
            taken_clothes = give_clothes(right_choice)
            timelist.append("Комплект на весь день")
            for item in taken_clothes:
                timelist.append(item)
            output = "\n".join(timelist)
            await message.channel.send(output)


client.run(settings['token'])
