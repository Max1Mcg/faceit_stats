Данный проект является десктопно-консольным аналогом сайт https://www.faceit-stats.me/, предназначенного для просмотра и анализа последних 20-и матчей по CS:GO на сайте faceit.
Для работы должен быть установлен пакет requests, python 3.7. При запуска приложение нужно указать никнейм для поиска, а затем получить подробную статистику за последние 20 матчей или же сообщение о её отсутствии.
Возможные причины отсутствия - пользователя с данным никнеймом нет на сайте; пользователь с данным никнеймом есть на сайте, но не играет в CS:GO; пользователь играет в CS:G0, но сыграл менее 20-и матчей;
Если матч является не рейтинговым, то это будет явно указано при выводе и не пойдёт в статистику.
Пример ввода:'Max1Mcg-', без кавычек
Данные получаются с помощью API сайта faceit.
