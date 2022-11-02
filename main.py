import requests
import json

"""класс, хранящий всю нужную информацию для текущего игрока
    """


class Player:
    def __init__(self, all_info, faceit_analysis):
        self.nickname = all_info['nickname']
        self.player_id = all_info['player_id']
        self.matches_personal = faceit_analysis.last_matches(self.player_id, 0, 20)
        self.stats = {}
        self.stats['level'] = all_info['games']['csgo']['skill_level']
        self.stats['elo'] = all_info['games']['csgo']['faceit_elo']

    """Класс, который реализует весь функционал приложения
    """


class Faceit_analysis:
    """Конструктор, тут указывается существующий api_token для
    получения доступа к БД и headers для успешной авторизации
    """

    def __init__(self, api_token):
        self.name = "Faceit analysis";
        self.api_token = api_token
        self.base_url = "https://open.faceit.com/data/v4"
        self.headers = {
            'accept': 'application/json',
            'Authorization': 'Bearer {}'.format(self.api_token)
        }

    """Метод, классифицирующий статистику
    """

    def stats_computing(self, player):
        err_counter = 0
        player.stats['k_d'] = 0
        player.stats['aces'] = 0
        player.stats['avg_kills'] = 0
        player.stats['hs_rate'] = 0
        player.stats['leaves_time'] = 0
        player.stats_per_match = []
        for i in player.matches_personal['items']:
            player.stats_per_match.append({})
            if i['competition_name'] == '5v5 RANKED' and i['competition_type'] == 'matchmaking':
                player.stats['leaves_time'] += 1
                for j in self.stats_from_player_matches(i)['rounds'][0]['teams']:
                    if 'score' in player.stats_per_match[len(player.stats_per_match) - 1].keys():
                        player.stats_per_match[len(player.stats_per_match) - 1]['score'] += (
                        j['team_stats']['Final Score'])
                    else:
                        player.stats_per_match[len(player.stats_per_match) - 1]['score'] = j['team_stats'][
                                                                                               'Final Score'] + ":"
                    for k in j['players']:
                        if k['nickname'] == player.nickname:
                            if j['team_stats']['Team Win'] == '1':
                                player.stats_per_match[len(player.stats_per_match) - 1]['result'] = 'win'
                            else:
                                player.stats_per_match[len(player.stats_per_match) - 1]['result'] = 'lose'
                            player.stats['leaves_time'] -= 1
                            player.stats['k_d'] += float(k['player_stats']['K/D Ratio'])
                            player.stats['aces'] += int(k['player_stats']['Penta Kills'])
                            player.stats['avg_kills'] += float(k['player_stats']['Kills'])
                            player.stats['hs_rate'] += float(k['player_stats']['Headshots %'])
                            player.stats_per_match[len(player.stats_per_match) - 1]['K/D Ratio'] = float(
                                k['player_stats']['K/D Ratio'])
                            player.stats_per_match[len(player.stats_per_match) - 1]['aces'] = int(
                                k['player_stats']['Penta Kills'])
                            player.stats_per_match[len(player.stats_per_match) - 1]['kills'] = float(
                                k['player_stats']['Kills'])
                            player.stats_per_match[len(player.stats_per_match) - 1]['hs_rate'] = float(
                                k['player_stats']['Headshots %'])
            else:
                player.stats_per_match[len(player.stats_per_match) - 1][
                    'err'] = 'Данный матч был турнирный или не в режиме CS:GO 5v5'
                err_counter += 1
        player.stats['hs_rate'] /= (len(player.matches_personal['items']) - player.stats['leaves_time'] - err_counter)
        player.stats['avg_kills'] /= (len(player.matches_personal['items']) - player.stats['leaves_time'] - err_counter)
        player.stats['k_d'] /= (len(player.matches_personal['items']) - player.stats['leaves_time'] - err_counter)

    """Метод, возвращающий обработанную статистику пользователя
    """

    def get_stats_for_cur_player(self, player):
        print('Статистика последних {} матчей'.format(len(player.stats_per_match)))
        for i in player.stats_per_match:
            str_f_print = ""
            for j in i.keys():
                str_f_print += j + " = " + str(i[j]) + '\t'
            if len(i.keys()) == 1 and not ('err' in i.keys()):
                print(str_f_print + '\t' + 'LEAVER')
            else:
                print(str_f_print)
        print()
        print('Общая статистика за последние {} матчей'.format(len(player.stats_per_match)))
        for i in player.stats.keys():
            print(i + " = " + str(player.stats[i]) + '\t')

    """Метод, возвращающий название проекта
    """

    def name_of_project(self):
        return self.name;

    """Метод, выводящий краткую информацию по использованию приложения
    """

    def short_guide(self):
        guide = """Введите никнейм игрока на фэйсите и нажмите enter. Если никнейм введен иначе, то вам 
выдастся некоторая статистика по нему и его последним играм, иначе будет выдана ошибка. Регистр при 
написании никнейма важен."""
        return guide

    """Метод, выводящий некоторую информацию о возможности связаться с создателями приложения
    """

    def our_contacts(self):
        contacts = "email: leggo2001@mail.ru"
        return contacts

    """Метод, выбирающий [offset;limit] последних матчей
    """

    def last_matches(self, player_id, offset, limit):
        api_url = '{}/players/{}/history?game={}&offset={}&limit={}'.format(self.base_url, player_id, 'csgo',
                                                                            offset, limit)
        r = requests.get(api_url, headers=self.headers)
        return json.loads(r.content.decode('utf-8'))

    """Метод, находящий игрока по никнейму или выдающий сообщению, что никнейм введен неверно
    """

    def try_find_user(self, nickname):
        api_url = "{}/players".format(self.base_url)
        api_url += "?nickname={}".format(nickname)
        r = requests.get(api_url, headers=self.headers)
        if r.status_code == 200:
            player = Player(json.loads(r.content.decode('utf-8')), self)
            if len(player.matches_personal['items']) != 0:
                self.stats_computing(player)
                self.get_stats_for_cur_player(player)
            else:
                print('За последний месяц матчей сыграно не было!')
        else:
            print("Никнейм введен неверно")
            return None

    """Метод, собирающий всю статистику за [offset;limit] матчи
    """

    def stats_from_player_matches(self, cur_match):
        api_url = "{}/matches/{}/stats".format(self.base_url, cur_match['match_id'])
        r = requests.get(api_url, headers=self.headers)
        return (json.loads(r.content.decode('utf-8')))

    """Метод, получающий общую информацию о матче
    """

    def stats_per_match(self, match_id):
        api_url = "{}/matches/{}".format(self.base_url, match_id)
        r = requests.get(api_url, headers=self.headers)
        return (json.loads(r.content.decode('utf-8')))

    """Функция, заставляющая работать консольное приложение
    """


def app():
    application = Faceit_analysis('589a4e96-6431-42ea-bd6d-595228c27163')
    nickname = ""
    while nickname != 'END':
        print('Введите никнейм на фэйсите для поиска, ввод END соответствует прекращению работы программы')
        nickname = input()
        if nickname != 'END':
            application.try_find_user(nickname)
            print()
    print('Спасибо за использование!!!')
    return


app()
