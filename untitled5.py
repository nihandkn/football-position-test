from flask import Flask, request, render_template_string
import csv
import os
import socket
import qrcode
from datetime import datetime


app = Flask(__name__)


# ============================================================
# POZİSYONLAR
# ============================================================

POSITION_NAMES = {
    "QB": "Quarterback",
    "RB": "Running Back",
    "WR": "Wide Receiver",
    "TE": "Tight End",
    "OL": "Offensive Line",
    "DL": "Defensive Line",
    "LB": "Linebacker",
    "DB": "Defensive Back"
}


POSITION_DESCRIPTIONS = {

    "QB":
        "Pas yeteneği, oyun görüşü ve hızlı karar verme "
        "becerisinin ön planda olduğu pozisyon.",

    "RB":
        "Hız, patlayıcılık, çeviklik ve temas altında "
        "koşabilmenin önemli olduğu pozisyon.",

    "WR":
        "Hız, çeviklik ve top yakalama becerisinin "
        "ön plana çıktığı pozisyon.",

    "TE":
        "Güç ve top yakalama yeteneğinin birlikte "
        "kullanıldığı hibrit pozisyon.",

    "OL":
        "Güç, denge ve rakibi kontrol etmenin "
        "önemli olduğu pozisyon.",

    "DL":
        "Patlayıcı güç ve fiziksel mücadele ile "
        "rakip hücum hattına baskı yapan pozisyon.",

    "LB":
        "Hız, güç, tackling ve oyun görüşünün "
        "bir arada kullanıldığı savunma pozisyonu.",

    "DB":
        "Hız, çeviklik, reaksiyon ve coverage "
        "becerilerinin önemli olduğu savunma pozisyonu."
}


# ============================================================
# SORULAR
# Her soruda sadece 3 seçenek var.
# ============================================================

QUESTIONS = [

    {
        "question": "Koşu hızın nasıl?",
        "subtitle": "Kendini yaşıtlarınla karşılaştır.",
        "answers": {

            "İyi": {
                "WR": 5,
                "DB": 5,
                "RB": 4,
                "LB": 2
            },

            "Orta": {
                "QB": 2,
                "TE": 2,
                "LB": 2,
                "RB": 1
            },

            "Kötü": {
                "OL": 4,
                "DL": 4
            }
        }
    },

    {
        "question": "Çevikliğin nasıl?",
        "subtitle": "Ani yön değiştirme ve denge becerini düşün.",
        "answers": {

            "İyi": {
                "DB": 5,
                "RB": 5,
                "WR": 4
            },

            "Orta": {
                "LB": 2,
                "QB": 2,
                "TE": 2
            },

            "Kötü": {
                "OL": 4,
                "DL": 3
            }
        }
    },

    {
        "question": "Fiziksel gücün nasıl?",
        "subtitle": "İtme, çekme ve temas altında kalabilme gücünü düşün.",
        "answers": {

            "İyi": {
                "OL": 5,
                "DL": 5,
                "LB": 4,
                "TE": 3
            },

            "Orta": {
                "RB": 2,
                "TE": 2,
                "LB": 2,
                "QB": 1
            },

            "Kötü": {
                "WR": 3,
                "DB": 3,
                "QB": 2
            }
        }
    },

    {
        "question": "Top yakalama becerin nasıl?",
        "subtitle": "Hızlı ve zor gelen topları düşün.",
        "answers": {

            "İyi": {
                "WR": 5,
                "TE": 5,
                "RB": 3,
                "DB": 2
            },

            "Orta": {
                "RB": 2,
                "DB": 1,
                "LB": 1
            },

            "Kötü": {
                "OL": 3,
                "DL": 3
            }
        }
    },

    {
        "question": "Pas atma becerin nasıl?",
        "subtitle": "Kol gücü ve isabet oranını birlikte düşün.",
        "answers": {

            "İyi": {
                "QB": 7
            },

            "Orta": {
                "QB": 3
            },

            "Kötü": {
                "RB": 1,
                "WR": 1,
                "DB": 1,
                "OL": 1,
                "DL": 1
            }
        }
    },

    {
        "question": "Temaslı oyunda nasılsın?",
        "subtitle": "Tackle ve fiziksel mücadeleyi düşün.",
        "answers": {

            "İyi": {
                "LB": 5,
                "DL": 5,
                "OL": 4,
                "RB": 2
            },

            "Orta": {
                "TE": 3,
                "RB": 3,
                "DB": 2
            },

            "Kötü": {
                "WR": 3,
                "QB": 3
            }
        }
    },

    {
        "question": "Karar verme hızın nasıl?",
        "subtitle": "Baskı altında hızlı karar vermeyi düşün.",
        "answers": {

            "İyi": {
                "QB": 5,
                "LB": 3,
                "DB": 3
            },

            "Orta": {
                "RB": 2,
                "WR": 2,
                "TE": 2
            },

            "Kötü": {
                "OL": 2,
                "DL": 2
            }
        }
    },

    {
        "question": "Patlayıcı gücün nasıl?",
        "subtitle": "İlk birkaç adımda hızlanma becerini düşün.",
        "answers": {

            "İyi": {
                "RB": 5,
                "DL": 5,
                "WR": 4,
                "DB": 3
            },

            "Orta": {
                "LB": 3,
                "TE": 2,
                "QB": 2
            },

            "Kötü": {
                "OL": 3
            }
        }
    },

    {
        "question": "Dayanıklılığın nasıl?",
        "subtitle": "Yüksek tempoda tekrar tekrar hareket edebilmek.",
        "answers": {

            "İyi": {
                "DB": 4,
                "WR": 4,
                "LB": 4,
                "RB": 3
            },

            "Orta": {
                "TE": 2,
                "QB": 2,
                "DL": 2
            },

            "Kötü": {
                "OL": 2,
                "DL": 1
            }
        }
    },

    {
        "question": "Oyun görüşün nasıl?",
        "subtitle": "Sahada olup biteni okuyabilme becerini düşün.",
        "answers": {

            "İyi": {
                "QB": 5,
                "LB": 4,
                "DB": 3
            },

            "Orta": {
                "RB": 2,
                "WR": 2,
                "TE": 2
            },

            "Kötü": {
                "OL": 2,
                "DL": 2
            }
        }
    }

]


# ============================================================
# HTML + CSS
# ============================================================

PAGE_TEMPLATE = """
<!DOCTYPE html>

<html lang="tr">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width,
initial-scale=1.0,
maximum-scale=1.0">

<title>Football Position Test</title>

<style>

* {
    box-sizing: border-box;
}

body {

    margin: 0;

    background: #050505;

    color: white;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    min-height: 100vh;

}

.container {

    width: 92%;

    max-width: 520px;

    margin: auto;

    padding:
        35px
        18px
        50px
        18px;

}

.logo {

    color: #800020;

    font-weight: 900;

    font-size: 15px;

    letter-spacing: 4px;

    margin-bottom: 30px;

}

h1 {

    font-size: 36px;

    line-height: 1.05;

    margin-bottom: 15px;

}

.subtitle {

    color: #999;

    line-height: 1.5;

    margin-bottom: 35px;

}

input,
select {

    width: 100%;

    padding: 18px;

    margin-bottom: 14px;

    background: #111;

    border:
        1px solid
        #333;

    color: white;

    border-radius: 8px;

    font-size: 17px;

}

input:focus,
select:focus {

    outline: none;

    border-color: #800020;

}

button {

    width: 100%;

    padding: 19px;

    border: none;

    border-radius: 8px;

    background: #800020;

    color: white;

    font-weight: bold;

    font-size: 18px;

    cursor: pointer;

    margin-top: 10px;

}

button:hover {

    background: #a00028;

}

.answer {

    display: block;

    background: #111;

    border:
        2px solid
        #800020;

    border-radius: 10px;

    padding: 20px;

    margin: 14px 0;

    font-size: 19px;

    font-weight: bold;

    cursor: pointer;

    transition: 0.2s;

}

.answer:hover {

    background: #800020;

}

.answer input {

    display: none;

}

.answer:has(input:checked) {

    background: #800020;

}

.progress-background {

    width: 100%;

    height: 6px;

    background: #222;

    margin-bottom: 35px;

    border-radius: 100px;

    overflow: hidden;

}

.progress {

    height: 100%;

    background: #800020;

}

.question-number {

    color: #800020;

    font-size: 13px;

    font-weight: bold;

    letter-spacing: 2px;

    margin-bottom: 10px;

}

.question-title {

    font-size: 27px;

    font-weight: 800;

    line-height: 1.2;

}

.result-title {

    color: #888;

    letter-spacing: 3px;

    font-size: 13px;

}

.position {

    color: #800020;

    font-size: 45px;

    font-weight: 900;

    margin:
        8px
        0;

}

.position-full {

    font-size: 23px;

    margin-bottom: 25px;

}

.result-description {

    color: #bbb;

    font-size: 16px;

    line-height: 1.6;

    margin-bottom: 35px;

}

.ranking {

    background: #111;

    padding: 18px;

    border-radius: 8px;

    margin-bottom: 12px;

    border-left:
        5px solid
        #800020;

}

.percent {

    color: #800020;

    font-weight: bold;

    float: right;

}

.name {

    color: #aaa;

    margin-bottom: 30px;

}

.footer {

    color: #555;

    text-align: center;

    font-size: 12px;

    margin-top: 40px;

}

</style>

</head>


<body>

<div class="container">

{% if page == "start" %}


<div class="logo">
FOOTBALL POSITION TEST
</div>


<h1>
Hangi pozisyonda<br>
oynamalısın?
</h1>


<div class="subtitle">

Fiziksel özelliklerini ve
oyun tarzını değerlendir.

Test sonunda sana en uygun
Amerikan futbolu pozisyonunu
bulalım.

</div>


<form method="POST"
action="/quiz">


<input
type="text"
name="name"
placeholder="Ad"
required>


<input
type="text"
name="surname"
placeholder="Soyad"
required>


<input
type="text"
name="class_name"
placeholder="Sınıf"
required>


<button type="submit">
TESTE BAŞLA
</button>


</form>


{% endif %}



{% if page == "quiz" %}


<div class="logo">
FOOTBALL POSITION TEST
</div>


<form method="POST"
action="/result">


<input type="hidden"
name="name"
value="{{ name }}">


<input type="hidden"
name="surname"
value="{{ surname }}">


<input type="hidden"
name="class_name"
value="{{ class_name }}">


{% for q in questions %}


<div class="question-block">


<div class="question-number">

SORU {{ loop.index }}
/
{{ questions|length }}

</div>


<div class="progress-background">

<div class="progress"
style="width:
{{ (loop.index / questions|length) * 100 }}%">
</div>

</div>


<div class="question-title">

{{ q.question }}

</div>


<div class="subtitle">

{{ q.subtitle }}

</div>


{% for answer in q.answers.keys() %}


<label class="answer">

<input
type="radio"
name="q{{ loop.index0 }}"
value="{{ answer }}"
required>

{{ answer }}

</label>


{% endfor %}


<br><br><br>


</div>


{% endfor %}


<button type="submit">

SONUCU GÖSTER

</button>


</form>


{% endif %}



{% if page == "result" %}


<div class="logo">

FOOTBALL POSITION TEST

</div>


<div class="result-title">

SONUCUN

</div>


<div class="position">

{{ best_position }}

</div>


<div class="position-full">

{{ best_name }}

</div>


<div class="name">

{{ name }}
{{ surname }}
•
{{ class_name }}

</div>


<div class="result-description">

{{ description }}

</div>


<h3>
EN UYGUN 3 POZİSYON
</h3>


{% for result in top_three %}


<div class="ranking">

<strong>

#{{ loop.index }}

{{ result[1] }}

</strong>


<span class="percent">

{{ result[2] }}%

</span>


</div>


{% endfor %}


<br>


<a href="/">

<button>

TESTİ TEKRARLA

</button>

</a>


{% endif %}


<div class="footer">

AMERICAN FOOTBALL
POSITION TEST

</div>


</div>

</body>

</html>
"""


# ============================================================
# ANA SAYFA
# ============================================================

@app.route("/")
def start():

    return render_template_string(
        PAGE_TEMPLATE,
        page="start"
    )


# ============================================================
# QUIZ
# ============================================================

@app.route("/quiz", methods=["POST"])
def quiz():

    name = request.form.get("name")

    surname = request.form.get("surname")

    class_name = request.form.get("class_name")

    return render_template_string(

        PAGE_TEMPLATE,

        page="quiz",

        name=name,

        surname=surname,

        class_name=class_name,

        questions=QUESTIONS

    )


# ============================================================
# SONUÇ
# ============================================================

@app.route("/result", methods=["POST"])
def result():

    name = request.form.get("name")

    surname = request.form.get("surname")

    class_name = request.form.get("class_name")


    scores = {

        "QB": 0,

        "RB": 0,

        "WR": 0,

        "TE": 0,

        "OL": 0,

        "DL": 0,

        "LB": 0,

        "DB": 0

    }


    for index, question in enumerate(QUESTIONS):

        answer = request.form.get(
            f"q{index}"
        )

        if answer:

            points = question[
                "answers"
            ][answer]

            for position, value in points.items():

                scores[position] += value


    sorted_scores = sorted(

        scores.items(),

        key=lambda x: x[1],

        reverse=True

    )


    best_position = sorted_scores[0][0]

    max_score = sorted_scores[0][1]


    top_three = []


    for position, score in sorted_scores[:3]:

        if max_score == 0:

            percentage = 0

        else:

            percentage = round(
                score
                /
                max_score
                *
                100
            )


        top_three.append(

            (

                position,

                POSITION_NAMES[position],

                percentage

            )

        )


    save_result(

        name,

        surname,

        class_name,

        best_position,

        scores

    )


    return render_template_string(

        PAGE_TEMPLATE,

        page="result",

        name=name,

        surname=surname,

        class_name=class_name,

        best_position=best_position,

        best_name=
            POSITION_NAMES[
                best_position
            ],

        description=
            POSITION_DESCRIPTIONS[
                best_position
            ],

        top_three=top_three

    )


# ============================================================
# CSV'YE KAYDET
# ============================================================

def save_result(
        name,
        surname,
        class_name,
        position,
        scores):


    file_exists = os.path.exists(
        "results.csv"
    )


    with open(
        "results.csv",
        "a",
        newline="",
        encoding="utf-8"
    ) as file:


        writer = csv.writer(file)


        if not file_exists:

            writer.writerow([

                "Tarih",

                "Ad",

                "Soyad",

                "Sınıf",

                "Sonuç",

                "QB",

                "RB",

                "WR",

                "TE",

                "OL",

                "DL",

                "LB",

                "DB"

            ])


        writer.writerow([

            datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            ),

            name,

            surname,

            class_name,

            position,

            scores["QB"],

            scores["RB"],

            scores["WR"],

            scores["TE"],

            scores["OL"],

            scores["DL"],

            scores["LB"],

            scores["DB"]

        ])


# ============================================================
# IP ADRESİNİ BUL
# ============================================================

def get_local_ip():

    s = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    try:

        s.connect(
            ("8.8.8.8", 80)
        )

        ip = s.getsockname()[0]

    except:

        ip = "127.0.0.1"

    finally:

        s.close()

    return ip


# ============================================================
# QR KOD OLUŞTUR
# ============================================================

def create_qr(url):

    qr = qrcode.make(url)

    qr.save(
        "football_quiz_qr.png"
    )


# ============================================================
# PROGRAMI ÇALIŞTIR
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)