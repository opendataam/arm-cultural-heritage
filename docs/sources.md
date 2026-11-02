# Структура `data/sources.csv`

`data/sources.csv` — машиночитаемый реестр источников материалов о культурном наследии Армении и армянского народа. Он фиксирует, где находятся данные, как их получить, на каких условиях их можно использовать и в каком состоянии находится интеграция. Человекочитаемое описание тех же источников находится в [`armenian_data_sources.md`](armenian_data_sources.md).

Машинно-читаемая схема строки находится в [`schema/sources.schema.json`](../schema/sources.schema.json). Она использует JSON Schema 2020-12 и применяется к объекту, полученному из одной CSV-строки. Поле `x-csv.columns` фиксирует порядок колонок.

## Формат файла

- Кодировка: UTF-8.
- Разделитель: запятая.
- Заголовок обязателен и должен точно соответствовать порядку ниже.
- Строки отсортированы по `id`.
- Списки внутри ячейки разделяются точкой с запятой без пробелов: `books;periodicals`.
- Все колонки присутствуют всегда; необязательные значения могут быть пустыми строками.
- Генерируемые файлы используют LF. Начальные и конечные пробелы значений удаляются при чтении.

```csv
id,name,name_local,url,country,institution_type,scope,integration,content_types,languages,est_armenian_items,count_note,access_methods,endpoint,auth,metadata_format,metadata_license,content_rights,commercial_use,attribution_required,automated_access,terms_url,terms_summary,priority,status,verified_at,notes
```

## Колонки

### Идентификация

| Колонка | Обязательна | Назначение |
| --- | --- | --- |
| `id` | да | Стабильный ID: префикс страны в нижнем регистре или `int`/`eu`, точка, короткое имя (`am.arar`, `eu.europeana`, `int.wikidata`) |
| `name` | да | Официальное название на английском |
| `name_local` | нет | Название на языке учреждения |
| `url` | да | Главная страница |
| `country` | да | Страна местонахождения, ISO 3166-1 alpha-2 (`AM`, `RU`, `FR`) |
| `institution_type` | да | `library`, `archive`, `museum`, `aggregator`, `digital_library`, `research_institute`, `religious`, `foundation`, `media`, `registry`, `portal`, `authority` |

Префикс `id` не обязан совпадать с `country`: международные проекты используют `int`, а `country` указывает юридическое местонахождение.

### Охват и способ интеграции

| Колонка | Значения | Назначение |
| --- | --- | --- |
| `scope` | `dedicated`, `mixed`, `reference` | Профильный армянский источник, общий фонд с армянскими записями или справочник |
| `integration` | `harvest`, `filter`, `link`, `none` | Как источник встраивается в проект |
| `content_types` | список | `manuscripts`, `books`, `periodicals`, `articles`, `archives`, `photographs`, `artworks`, `objects`, `maps`, `audio`, `video`, `oral_history`, `monuments`, `texts`, `ephemera`, `authority` |
| `languages` | список ISO 639 | Языки метаданных, а не языки самих материалов |
| `est_armenian_items` | целое или пусто | Оценка числа армянских записей |
| `count_note` | текст | Что, где и когда посчитано; обязательно при заполненном `est_armenian_items` |

Способы интеграции:

- `harvest` — источник целиком армянский, записи забираются полностью без matcher;
- `filter` — общий фонд, армянские записи отбираются matcher-ом и реестром `data/terms.csv`, как для Госкаталога;
- `link` — источник используется для связывания, обогащения или внешних ссылок, записи не импортируются как объекты;
- `none` — организация не публикует метаданные (фонд, издатель, исследовательский центр); строка сохраняется для полноты, `status` всегда `not-applicable`.

### Доступ

| Колонка | Значения | Назначение |
| --- | --- | --- |
| `access_methods` | список | `api`, `oai-pmh`, `iiif`, `sru`, `z39.50`, `sparql`, `bulk`, `web`, `none` |
| `endpoint` | URL или пусто | Лучшая машинная точка доступа |
| `auth` | `none`, `key`, `registration`, `restricted` | Требования к доступу |
| `metadata_format` | список | `edm`, `dc`, `qdc`, `marc`, `mods`, `mets`, `lido`, `ead`, `iiif`, `json`, `csv`, `rdf`, `html`, `other` |

`none` в `access_methods` не сочетается с другими значениями. Для `harvest` и `filter` нужен хотя бы один способ доступа. `web` означает, что данные доступны только через HTML-страницы и требуют скрейпинга.

### Условия использования

| Колонка | Значения | Назначение |
| --- | --- | --- |
| `metadata_license` | SPDX-ID, `public-domain`, `custom`, `all-rights-reserved`, `unknown` | Лицензия метаданных |
| `content_rights` | `public-domain`, `open`, `mixed`, `restricted`, `all-rights-reserved`, `unknown` | Права на изображения, тексты и записи в целом по источнику |
| `commercial_use` | `yes`, `no`, `conditional`, `unknown` | Допускается ли коммерческое использование |
| `attribution_required` | `yes`, `no`, `unknown` | Требуется ли указание источника |
| `automated_access` | `allowed`, `api-only`, `restricted`, `prohibited`, `unknown` | Допустим ли автоматический сбор |
| `terms_url` | URL или пусто | Страница условий; обязательна, если `metadata_license` не `unknown` |
| `terms_summary` | текст | Краткое изложение условий на английском |

Допустимые SPDX-значения: `CC0-1.0`, `CC-BY-4.0`, `CC-BY-SA-4.0`, `CC-BY-NC-4.0`, `CC-BY-NC-SA-4.0`, `CC-BY-NC-ND-4.0`, `ODbL-1.0`, `ODC-By-1.0`, `PDDL-1.0`.

`custom` означает собственные условия учреждения без стандартной лицензии. `unknown` означает, что условия не опубликованы или не найдены; такие источники нельзя публиковать дальше без запроса разрешения. Уровень источника не заменяет права отдельной записи: при импорте нужно сохранять rights statement каждой записи, если источник его предоставляет.

### Планирование

| Колонка | Значения | Назначение |
| --- | --- | --- |
| `priority` | `1`–`4` | 1 — MVP; 2 — ближайшая очередь; 3 — нужны переговоры, ключи или скрейпинг; 4 — справочно или без интеграции |
| `status` | `integrated`, `planned`, `candidate`, `blocked`, `not-applicable` | Состояние интеграции |
| `verified_at` | `YYYY-MM-DD` | Дата последней проверки |
| `notes` | текст | Платформа, блокеры, пересечения |

`integrated` допустим только для `harvest` и `filter`.

## Проверка

```bash
python3 scripts/sources.py data/sources.csv
python3 -m pytest -q tests/test_sources.py
```

Валидатор проверяет заголовок и порядок колонок, обязательные значения, перечисления и списки, формат ID, кодов стран и языков, URL, дату, уникальность ID и согласованность полей. Тесты сверяют JSON Schema с константами валидатора и проверяют, что MVP охватывает больше одного источника и больше одного языка.

Сведения об условиях использования устаревают. Перед подключением источника нужно перепроверить `terms_url` и обновить `verified_at`.
