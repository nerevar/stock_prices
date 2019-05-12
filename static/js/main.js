/**
 * Преобразует данные из csv в массив значений
 * Для каждой строки (точки на графике) возвращает время и значение в этой точке (ровно одно значение)
 * @param {String} csv - строка с данными графика в формате: "timestamp,value1,<value2>,..."
 * @param {Number} [valueIndex] - порядковый номер `Значения` в массиве значений.
 *      По-умолчанию берётся первое. Нумерация с 1
 * @returns {Array} - массив [[timestamp, value], ...]
 */
function parse_csv(csv, valueIndex) {
    valueIndex || (valueIndex = 1);
    var series = [];

    csv.split('\n').forEach(function (line) {
        var data = line.split(',');
        if (data.length >= 2) {
            var point = [];
            data.forEach(function(value, index) {
                if (index === 0 || index === valueIndex) {
                    point.push((value && value !== '\r') ? +value : null);
                }
            });
            series.push(point);
        }
    });
    // TODO: sort & uniq
    return series;
}

/**
 * Синтаксический сахар для аякса
 * @param {String} url
 * @returns {Promise}
 */
function loadData(url) {
    return $.ajax({
        type: 'GET',
        url: url
    })
}

/**
 * Хелпер для рисования графика
 * @param {Object} params - параметры графика
 */
function plotGraph(params) {
    var defaultParams = {
        title: {
            text: document.title,
            style: {fontSize: '24px'}
        },
        time: {useUTC: false},
        stockTools: {
            gui: {enabled: false}
        },
        tooltip: {
            shape: 'square',
            headerShape: 'callout',
            borderWidth: 0,
            shadow: false
        }
    };

    Highcharts.stockChart('container', $.extend(true, {}, defaultParams, params));
}

/**
 * Функция для объединения нескольких массивов данных в один.
 * Вызывает функцию `callback` для каждой точке, которая есть за определённую дату сразу во всех массивах
 * @param {Array} *data - массивы данных в формате [[timestamp, value], ...]
 * @param {Function} callback - функция-обработчик для каждой общей точки.
 *      На вход приходят значения нескольких массивов в одной точке
 *      На выходе ожидает значение или массив значений в точке
 *      Вызывается только для тех точек, у которых есть ВСЕ непустые значения
 */
function mergeData() {
    var args = [].slice.call(arguments);
    var callback = args.pop();

    // assert(typeof callback === 'function');
    // assert(args.length >= 2);

    var results_dict = {};
    args.forEach(function(data, i) {
        data.forEach(function(point) {
            if (!results_dict[point[0]]) {
                results_dict[point[0]] = [];
            }
            results_dict[point[0]][i] = point;
        });
    });

    return _(results_dict)
        .toArray()
        .filter(function(points){
            // удаляем точки, где не все данные есть
            return _.filter(points).length === args.length;
        })
        .sortBy(function(points) {
            // сортировка по дате
            return points[0][0];
        })
        .map(function(points) {
            // расчёт значения в каждой точке
            return [points[0][0]].concat(callback.apply(this, points));
        })
        .value();
}
