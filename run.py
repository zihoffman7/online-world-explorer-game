from flask import Flask, redirect, url_for, render_template, request, session, send_file, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from uuid import uuid4
from map import maps, pp as portal
import map as m
from json import dump, loads, dumps
from json.decoder import JSONDecodeError
from random import choice, randrange
from math import floor
from better_profanity import profanity
from skins import free_skins, skins as all_skins

app = Flask(__name__)
app.secret_key = "tan the man"
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.config["PERMANENT_SESSION_LIFETIME"] = True
socketio = SocketIO(app)

treasures = {
    "main": {
        "world": "main",
        "x": 0,
        "y": 0,
        "size": 1,
        "dir": "d",
        "shown": False
    },
    "pumpkin": [
        {
            "img": "skins/pumpkin.png", "size": 1.2, "points": 1,
            "spawnable": [m.g1, m.g2, m.g3, m.g4, m.p1, m.p2, m.p3],
            "worlds": ["main", "beach", "volcano"], "shown": False
        },
        {
            "img": "skins/pumpkin.png", "size": 1.12, "points": 1,
            "spawnable": [m.g1, m.g2, m.g3, m.g4, m.p1, m.p2, m.p3],
            "worlds": ["main", "beach", "volcano"], "shown": False
        },
        {
            "img": "skins/pumpkin.png", "size": 1.34, "points": 1,
            "spawnable": [m.g1, m.g2, m.g3, m.g4, m.p1, m.p2, m.p3],
            "worlds": ["main", "beach", "volcano"], "shown": False
        }
    ],
    "carrot": [
        {
            "img": "skins/carrot.png", "size": 1, "points": 1,
            "spawnable": [m.g1, m.g2], "worlds": ["main", "beach"], "shown": False
        },
        {
            "img": "skins/carrot.png", "size": 0.9, "points": 1,
            "spawnable": [m.g3], "worlds": ["main", "beach"], "shown": False
        }
    ],
    "orange": [
        {
            "img": "skins/orange.png", "size": 0.9, "points": 1,
            "spawnable": [m.s1, m.s2, m.s3, m.w1, m.w2],
            "worlds": ["main", "beach"], "shown": False
        },
        {
            "img": "skins/orange.png", "size": 0.95, "points": 1,
            "spawnable": [m.s1, m.s2, m.s3, m.w1, m.w2],
            "worlds": ["main", "cave"], "shown": False
        },
        {
            "img": "skins/orange.png", "size": 0.9, "points": 1,
            "spawnable": [m.s1, m.s2, m.s3, m.w1, m.w2, m.g1, m.g2, m.g3],
            "worlds": ["cave", "beach", "snow"], "shown": False
        }
    ],
    "mushroom": [
        {
            "img": "skins/mushroom.png", "size": 0.8, "points": 1,
            "spawnable": [m.s1, m.s2, m.s3], "worlds": ["cave"], "shown": False
        },
        {
            "img": "skins/mushroom.png", "size": 0.85, "points": 1,
            "spawnable": [m.s1, m.s2, m.s3], "worlds": ["cave"], "shown": False
        },
        {
            "img": "skins/mushroom.png", "size": 0.8, "points": 1,
            "spawnable": [m.p1, m.p2, m.p3], "worlds": ["mushroom"], "shown": False
        },
        {
            "img": "skins/mushroom.png", "size": 0.85, "points": 1,
            "spawnable": [m.p1, m.p2, m.p3], "worlds": ["mushroom"], "shown": False
        },
        {
            "img": "skins/mushroom.png", "size": 0.75, "points": 1,
            "spawnable": [m.p1, m.p2, m.p3], "worlds": ["mushroom"], "shown": False
        },
        {
            "img": "skins/mushroom.png", "size": 0.9, "points": 1,
            "spawnable": [m.p1, m.p2, m.p3], "worlds": ["mushroom"], "shown": False
        }
    ],
    "redshroom": [
        {
            "img": "skins/redshroom.png", "size": 0.9, "points": 1,
            "spawnable": [m.s1, m.s2, m.s3], "worlds": ["cave"], "shown": False
        },
        {
            "img": "skins/redshroom.png", "size": 0.85, "points": 1,
            "spawnable": [m.p1, m.p2, m.p3], "worlds": ["mushroom"], "shown": False
        },
        {
            "img": "skins/redshroom.png", "size": 0.95, "points": 1,
            "spawnable": [m.p1, m.p2, m.p3], "worlds": ["mushroom"], "shown": False
        }
    ],
    "melon": [
        {
            "img": "skins/melon.png", "size": 1.05, "points": 1,
            "spawnable": [m.p1, m.p2, m.p3], "worlds": ["beach", "main", "volcano"], "shown": False
        },
        {
            "img": "skins/melon.png", "size": 1.15, "points": 1,
            "spawnable": [m.p1, m.p2, m.p3], "worlds": ["beach", "volcano"], "shown": False
        },
        {
            "img": "skins/melon.png", "size": 1.25, "points": 1,
            "spawnable": [m.p1, m.p2, m.p3], "worlds": ["volcano"], "shown": False
        }
    ],
    "slice": [
        {
            "img": "skins/slice.png", "size": 1.15, "points": 0.8,
            "spawnable": [m.p1, m.p2, m.p3], "worlds": ["volcano"], "shown": False
        },
        {
            "img": "skins/slice.png", "size": 1.1, "points": 0.8,
            "spawnable": [m.p1, m.p2, m.p3], "worlds": ["volcano", "beach"], "shown": False
        },
    ],
    "acorn": [
        {
            "img": "skins/acorn.png", "size": 0.9, "points": 1,
            "spawnable": [m.g1, m.g2, m.g3, m.g4, m.w1, m.w2, m.w3], "worlds": ["main", "snow"], "shown": False
        },
        {
            "img": "skins/acorn.png", "size": 0.95, "points": 1,
            "spawnable": [m.g1, m.g2, m.g3, m.g4, m.w1, m.w2, m.w3], "worlds": ["main", "snow"], "shown": False
        },
        {
            "img": "skins/acorn.png", "size": 0.85, "points": 1,
            "spawnable": [m.g1, m.g2, m.g3, m.g4, m.w1, m.w2, m.w3], "worlds": ["main", "snow"], "shown": False
        },
    ],
    "berry": [
        {
            "img": "skins/berry.png", "size": 0.9, "points": 1,
            "spawnable": [m.g1, m.g2, m.g3, m.g4, m.w1, m.w2, m.w3], "worlds": ["main", "snow", "beach", "cloud"], "shown": False
        },
        {
            "img": "skins/berry.png", "size": 0.95, "points": 1,
            "spawnable": [m.g1, m.g2, m.g3, m.g4, m.w1, m.w2, m.w3], "worlds": ["main", "snow", "beach", "cloud"], "shown": False
        },
        {
            "img": "skins/berry.png", "size": 0.8, "points": 1,
            "spawnable": [m.g1, m.g2, m.g3, m.g4, m.w1, m.w2, m.w3], "worlds": ["main", "snow", "beach", "cloud"], "shown": False
        }
    ],
    "purpleberry": [
        {
            "img": "skins/purpleberry.png", "size": 0.9, "points": 1,
            "spawnable": [m.w1, m.w2, m.w3], "worlds": ["snow", "cloud"], "shown": False
        },
        {
            "img": "skins/purpleberry.png", "size": 0.95, "points": 1,
            "spawnable": [m.w1, m.w2, m.w3], "worlds": ["snow"], "shown": False
        },
        {
            "img": "skins/purpleberry.png", "size": 0.8, "points": 1,
            "spawnable": [m.w1, m.w2, m.w3], "worlds": ["snow", "cloud"], "shown": False
        }
    ],
    "coconut": [
        {
            "img": "skins/coconut.png", "size": 0.95, "points": 1,
            "spawnable": [m.s1, m.s2, m.s3, m.g1, m.g2, m.g3], "worlds": ["beach"], "shown": False
        },
        {
            "img": "skins/coconut.png", "size": 0.85, "points": 1,
            "spawnable": [m.s1, m.s2, m.s3, m.g1, m.g2, m.g3], "worlds": ["beach"], "shown": False
        }
    ],
    "pear": [
        {
            "img": "skins/pear.png", "size": 0.95, "points": 1,
            "spawnable": [m.g1, m.g2, m.g3], "worlds": ["main", "beach"], "shown": False
        },
        {
            "img": "skins/pear.png", "size": 1, "points": 1,
            "spawnable": [m.g1, m.g2, m.g3], "worlds": ["main"], "shown": False
        }
    ],
    "desertmelonslice": [
        {
            "img": "skins/desertmelonslice.png", "size": 1.15, "points": 1,
            "spawnable": [m.s1, m.s2, m.s3], "worlds": ["main", "cave", "main"], "shown": False
        },
        {
            "img": "skins/desertmelonslice.png", "size": 1.1, "points": 1,
            "spawnable": [m.s1, m.s2, m.s3], "worlds": ["main", "cave"], "shown": False
        }
    ],
    "carcass": [
        {
            "img": "skins/carcass.png", "size": 1.7, "points": 2,
            "spawnable": [m.a1, m.a2, m.a3], "worlds": ["abyss", "mushroom"], "shown": False
        },
        {
            "img": "skins/carcass4.png", "size": 1.9, "points": 3,
            "spawnable": [m.a1, m.a2, m.a3, m.g1, m.g2, m.g3, m.p1, m.p2, m.p3], "worlds": ["abyss", "main", "beach", "volcano", "mushroom"], "shown": False
        },
        {
            "img": "skins/carcass3.png", "size": 2.4, "points": 4,
            "spawnable": [m.a1, m.a2, m.a3, m.g1, m.g2, m.g3, m.w1, m.w2, m.w3, m.s1, m.s2, m.s3, m.p1, m.p2, m.p3], "worlds": ["mushroom", "main", "volcano", "beach", "snow"], "shown": False
        },
        {
            "img": "skins/carcass2.png", "size": 1.9, "points": 2.5,
            "spawnable": [m.a1, m.a2, m.a3, m.g1, m.g2, m.g3, m.w1, m.w2, m.w3], "worlds": ["abyss", "main", "beach", "snow"], "shown": False
        }
    ],
    "meat": [
        {
            "img": "skins/meat.png", "size": 1.1, "points": 4,
            "spawnable": [m.g1, m.g2, m.g3, m.w1, m.w2, m.w3, m.s1, m.s2, m.s3, m.s1, m.s2, m.s3, m.p1, m.p2, m.p3], "worlds": ["main", "volcano", "snow", "cave", "beach"], "shown": False
        },
        {
            "img": "skins/meat.png", "size": 0.9, "points": 4,
            "spawnable": [m.g1, m.g2, m.g3, m.w1, m.w2, m.w3, m.s1, m.s2, m.s3, m.s1, m.s2, m.s3, m.p1, m.p2, m.p3], "worlds": ["main", "volcano", "snow", "cave", "beach"], "shown": False
        }
    ],
    "treasure": [
        {
            "img": "skins/treasure.png", "size": 0.8, "points": 2,
            "spawnable": [m.a1, m.a2, m.a3, m.s1, m.s2, m.s3], "worlds": ["treasure"], "shown": False
        },
        {
            "img": "skins/treasure.png", "size": 1.3, "points": 2,
            "spawnable": [m.a1, m.a2, m.a3, m.s1, m.s2, m.s3], "worlds": ["treasure"], "shown": False
        },
        {
            "img": "skins/treasure.png", "size": 1.05, "points": 2,
            "spawnable": [m.a1, m.a2, m.a3, m.s1, m.s2, m.s3], "worlds": ["treasure"], "shown": False
        },
        {
            "img": "skins/treasure.png", "size": 1.05, "points": 2,
            "spawnable": [m.r1, m.r2, m.r3, m.r4, m.b1, m.b2, m.b3, m.l1, m.l2, m.l3], "worlds": ["cursed"], "shown": False
        },
        {
            "img": "skins/treasure.png", "size": 1.05, "points": -2,
            "spawnable": [m.r1, m.r2, m.r3, m.r4, m.b1, m.b2, m.b3, m.l1, m.l2, m.l3], "worlds": ["cursed"], "shown": False
        }
    ]
}

def spawn_treasure():
    treasures["main"]["world"] = choice(tuple(filter(lambda x: "hidden" not in maps[x], list(maps.keys()))))
    while True:
        y = randrange(0, len(maps[treasures["main"]["world"]]["map"]))
        x = randrange(0, len(maps[treasures["main"]["world"]]["map"][y]))
        if maps[treasures["main"]["world"]]["elevation"][y][x] and type(maps[treasures["main"]["world"]]["map"][y][x]) != list:
            print(x, len(maps[treasures["main"]["world"]]["map"])-y, treasures["main"]["world"])
            treasures["main"]["x"] = x
            treasures["main"]["y"] = y
            treasures["main"]["size"] = 0.7 + randrange(110) / 100
            treasures["main"]["dir"] = choice(["d", "u", "l", "r"])
            treasures["main"]["shown"] = True
            break
    spawn_items()

def spawn_items():
    for item in sum(list(treasures.values())[1:], []):
        if not item["shown"]:
            c = 0
            item["world"] = choice(tuple(filter(lambda x: x in item["worlds"], list(maps.keys()))))
            while not item["shown"] and c < 50:
                c += 1
                y = randrange(0, len(maps[item["world"]]["map"]))
                x = randrange(0, len(maps[item["world"]]["map"][y]))
                if maps[item["world"]]["elevation"][y][x] and type(maps[item["world"]]["map"][y][x]) != list and maps[item["world"]]["map"][y][x] in item["spawnable"]:
                    item["x"] = x
                    item["y"] = y
                    if item["img"] == "skins/mushroom.png" or item["img"] == "skins/redshroom.png":
                        item["dir"] = "d"
                    else:
                        item["dir"] = choice(["d", "u", "l", "r"])
                    item["shown"] = True
            if c >= 50:
                item["world"] = "nan"

def save_session(score):
    with open("scores.json", "r+") as f:
        try:
            data = ""
            for char in f.read():
                if not ord(char) == 0:
                    data += char
            data = loads(data)
        except JSONDecodeError:
            data = {}
        f.truncate(0)
        data[session["id"]] = score
        dump(data, f)

def get_score(id, default):
    with open("scores.json", "r+") as f:
        try:
            data = ""
            for char in f.read():
                if not ord(char) == 0:
                    data += char
            data = loads(data)
        except JSONDecodeError:
            data = {}
        try:
            return data[id]
        except KeyError:
            return default

def add_skin(skin):
    with open("skins.json", "r+") as f:
        try:
            data = ""
            for char in f.read():
                if not ord(char) == 0:
                    data += char
            data = loads(data)
        except JSONDecodeError:
            data = {}
        f.truncate(0)
        if session["id"] in data.keys():
            data[session["id"]].insert(0, skin)
        else:
            data[session["id"]] = [skin]
        dump(data, f)

def get_skins(id):
    with open("skins.json", "r+") as f:
        try:
            data = ""
            for char in f.read():
                if not ord(char) == 0:
                    data += char
            data = loads(data)
        except JSONDecodeError:
            data = {}
        if id in data.keys():
            return {**{k: all_skins[k] for k in data[id]}, **{k: all_skins[k] for k in free_skins}}
        else:
            return {k: all_skins[k] for k in free_skins}

def move(player, dir, map_data):
    if dir in ["u", "d", "l", "r"]:
        old_y = player["locationY"]
        old_x = player["locationX"]

        player["chat"] = ""
        player["direction"] = dir
        if dir == "u":
            player["locationY"] -= 1
        elif dir == "d":
            player["locationY"] += 1
        elif dir == "l":
            player["locationX"] -= 1
        else:
            player["locationX"] += 1
        try:
            if map_data["elevation"][player["locationY"]][player["locationX"]] == "":
                player["locationY"] = old_y
                player["locationX"] = old_x
        except:
            pass
        finally:
            if player["locationX"] < 0 or player["locationY"] < 0 or player["locationX"] > len(map_data["map"][0])-1 or player["locationY"] > len(map_data["map"]) - 1:
                player["locationY"] = old_y
                player["locationX"] = old_x
            elif not old_y == player["locationY"] or not old_x == player["locationX"]:
                if "buffs" in all_skins[session["skin"]] and session["map"] in all_skins[session["skin"]]["buffs"].keys():
                    session["score"] += all_skins[session["skin"]]["buffs"][session["map"]]
                elif "score" in maps[session["map"]]:
                    session["score"] += maps[session["map"]]["score"]
                else:
                    session["score"] += 0.02
            if map_data["map"][player["locationY"]][player["locationX"]] == portal:
                warp(player, map_data)
            player["view_radius"] = map_data["elevation"][player["locationY"]][player["locationX"]]
            if session["map"] == treasures["main"]["world"] and player["locationX"] == treasures["main"]["x"] and player["locationY"] == treasures["main"]["y"]:
                emit("sound", "treasure", broadcast=False)
                if sum([len(i["players"]) for i in maps.values()]) * 6 > 60:
                    if choice([False, False, False, False, True]): # 20
                        session["score"] += sum([len(i["players"]) for i in maps.values()]) * 6 - 60
                    session["score"] += 60
                else:
                    session["score"] += sum([len(i["players"]) for i in maps.values()]) * 6
                spawn_treasure()
            for item in sum(list(treasures.values())[1:], []):
                if session["map"] == item["world"] and player["locationX"] == item["x"] and player["locationY"] == item["y"] and item["shown"]:
                    emit("sound", "food", broadcast=False)
                    session["score"] += item["points"]
                    if "buffs" in all_skins[session["skin"]] and session["map"] in all_skins[session["skin"]]["buffs"].keys():
                        session["score"] += (all_skins[session["skin"]]["buffs"][session["map"]] - 0.02) * 5
                    item["shown"] = False
            player["score"] = floor(session["score"])

def warp(player, map_data, t=False):
    r = maps[session["map"]]["players"][session["id"]]["radius"]
    d = maps[session["map"]]["players"][session["id"]]["direction"]
    maps[session["map"]]["players"].pop(session["id"])
    leave_room(session["map"])

    if t == "treasure":
        session["map"] = "treasure"
        x, y = 16, 39

    elif t == "mushroom":
        session["map"] = "mushroom"
        x, y = 15, 15
    elif t == "cursed":
        session["map"] = "cursed"
        x, y = 1, 1
    elif session["map"] == "main" and player["locationX"] == 69 and player["locationY"] == 9:
        session["map"] = "cloud"
        x, y = 28, 4
    elif session["map"] == "cloud" and player["locationX"] == 28 and player["locationY"] == 3:
        session["map"] = "main"
        x, y = 69, 10
    elif session["map"] == "main" and player["locationX"] == 2 and player["locationY"] == 43:
        session["map"] = "volcano"
        x, y = 49, 39
    elif session["map"] == "volcano" and player["locationX"] == 49 and player["locationY"] == 39 and player["direction"] == "d":
        session["map"] = "abyss"
        x, y = 11, 11
    elif session["map"] == "abyss" and player["locationX"] == 11 and player["locationY"] == 21 or session["map"] == "treasure" and player["locationX"] == 16 and player["locationY"] == 12 or session["map"] == "mushroom" and player["locationX"] == 25 and player["locationY"] == 10 or session["map"] == "cursed" and player["locationX"] == 40 and player["locationY"] == 32:
        if session["map"] == "mushroom":
            session["map"] = "cave"
        else:
            session["map"] = choice(tuple(filter(lambda x: "hidden" not in maps[x], list(maps.keys()))))
        while True:
            y = randrange(0, len(maps[session["map"]]["map"]))
            x = randrange(0, len(maps[session["map"]]["map"][y]))
            if maps[session["map"]]["elevation"][y][x] and type(maps[session["map"]]["elevation"][y][x]) != list:
                break
    elif session["map"] == "volcano" and player["locationX"] == 49 and player["locationY"] == 39:
        session["map"] = "main"
        x, y = 3, 43
    elif session["map"] == "volcano" and player["locationX"] == 48 and player["locationY"] == 15:
        session["map"] = "cloud"
        x, y = 4, 19
    elif session["map"] == "cloud" and player["locationX"] == 3 and player["locationY"] == 19:
        session["map"] = "volcano"
        x, y = 48, 16
    elif session["map"] == "main" and player["locationX"] == 6 and player["locationY"] == 2:
        session["map"] = "cave"
        x, y = 7, 45
    elif session["map"] == "cave" and player["locationX"] == 7 and player["locationY"] == 46:
        session["map"] = "main"
        x, y = 6, 3
    elif session["map"] == "main" and player["locationX"] == 54 and player["locationY"] == 2:
        session["map"] = "cave"
        x, y = 49, 45
    elif session["map"] == "cave" and player["locationX"] == 49 and player["locationY"] == 46:
        session["map"] = "main"
        x, y = 54, 3
    elif session["map"] == "main" and player["locationX"] == 61 and player["locationY"] == 33:
        session["map"] = "snow"
        x, y = 8, 42
    elif session["map"] == "snow" and player["locationX"] == 7 and player["locationY"] == 42:
        session["map"] = "main"
        x, y = 60, 33
    elif session["map"] == "snow" and player["locationX"] == 14 and player["locationY"] == 9:
        session["map"] = "cloud"
        x, y = 24, 17
    elif session["map"] == "cloud" and player["locationX"] == 24 and player["locationY"] == 18:
        session["map"] = "snow"
        x, y = 14, 10
    elif session["map"] == "snow" and player["locationX"] == 25 and player["locationY"] == 43:
        session["map"] = "beach"
        x, y = 42, 10
    elif session["map"] == "beach" and player["locationX"] == 42 and player["locationY"] == 9:
        session["map"] = "snow"
        x, y = 25, 42
    elif session["map"] == "beach" and player["locationX"] == 11 and player["locationY"] == 11:
        session["map"] = "cloud"
        x, y = 17, 28
    elif session["map"] == "cloud" and player["locationX"] == 17 and player["locationY"] == 29:
        session["map"] = "beach"
        x, y = 11, 12
    else:
        join_room(session["map"])
        print(player["locationX"])
        print(player["locationY"])
        return

    emit("stopsound", broadcast=False)

    if session["map"] == "cursed":
        emit("sound", "slider", broadcast=False)
    elif session["map"] == "treasure":
        emit("sound", "bonus", broadcast=False)
    elif session["map"] in ["cave", "mushroom"]:
        emit("sound", "cave", broadcast=False)
    elif session["map"] == "cloud":
        emit("sound", "overworld", broadcast=False)
    elif session["map"] == "main":
        emit("sound", "cloud", broadcast=False)
    elif session["map"] == "beach":
        emit("sound", "beach", broadcast=False)
    elif session["map"] == "volcano":
        emit("sound", "volcano", broadcast=False)
    elif session["map"] == "snow":
        emit("sound", "snow", broadcast=False)
    emit("sound", "teleport", broadcast=False)

    join_room(session["map"])
    maps[session["map"]]["players"][session["id"]] = {
        "name": session["name"], "locationX": x, "locationY": y,
        "radius": r, "direction": d, "chat": "",
        "view_radius": maps[session["map"]]["elevation"][y][x], "score": floor(session["score"]),
        "skin": {
            "width": all_skins[session["skin"]]["radius"],
            "name": session["skin"]
        }
    }

def chat(player, message):
    player["chat"] = message

def send(map_data):
    t = []
    if session["map"] == treasures["main"]["world"]:
        t = [treasures["main"]["x"], treasures["main"]["y"], treasures["main"]["size"], treasures["main"]["dir"]]
    others = []
    for item in sum(list(treasures.values())[1:], []):
        if item["world"] == session["map"] and item["shown"]:
            others.append(item)
    return {
        "boardColors": map_data["map"],
        "hidden": (lambda: not "hidden" in map_data.keys())(),
        "background": map_data["background"],
        "players": [map_data["players"]],
        "count": sum([len(i["players"]) for i in maps.values()]),
        "mapName": session["map"],
        "treasure": t,
        "items": others,
        "treasureData": f"{treasures['main']['world']} ({treasures['main']['x']}, {len(maps[treasures['main']['world']]['map']) - treasures['main']['y']})"
    }

@app.route("/", methods=["GET", "POST"])
def index():
    if not "id" in session:
        session["id"] = str(request.remote_addr)
        print(session["id"])
    session["score"] = get_score(session["id"], 0)
    if request.method == "POST":
        session["skin"] = request.form["skin"]
        print(session["skin"])
        if request.form["name"].strip() == "" or not profanity.censor(request.form["name"].strip()) == request.form["name"].strip():
            session["name"] = "User"
        else:
            session["name"] = request.form["name"]
        return redirect(url_for("game"))
    return render_template("name.html", skins=sorted([{"name":k, "path":v["path"], "cost": v["cost"]} for k,v in get_skins(session["id"]).items()], key=lambda d: d["cost"], reverse=True))

@app.route("/game", methods=["GET"])
def game():
    if not "score" in session:
        session["score"] = 0
    if not "name" in session or not "skin" in session:
        return redirect(url_for("index"))
    return render_template("index.html", skin=session["skin"], preload=dumps({**{k:v["path"] for k,v in all_skins.items()}, "treasure": "skins/treasure.png", **{i["img"].split("/")[-1].split(".")[0]: i["img"] for i in treasures["carcass"]}, **{k: v[0]["img"] for k, v in list(treasures.items())[1:]}} ))

@app.route("/skins", methods=["GET", "POSt"])
def skin_select():
    if not "id" in session:
        session["id"] = str(request.remote_addr)
    session["score"] = get_score(session["id"], 0)
    tcount = 0
    owned = [k for k in get_skins(session["id"]).keys()]
    for skin, v in all_skins.items():
        if "tiers" in v and skin in owned:
            tcount += 1
    if request.method == "POST":
        if all_skins[request.form["name"]]["cost"] <= session["score"]:
            if "tiers" in all_skins[request.form["name"]]:
                session["score"] -= all_skins[request.form["name"]]["tiers"][tcount]
            else:
                session["score"] -= all_skins[request.form["name"]]["cost"]
            add_skin(request.form["name"])
            save_session(session["score"])
            owned = [k for k in get_skins(session["id"]).keys()]
    avaliable = []
    for skin, v in all_skins.items():
        if "required" in v:
            for r in v["required"]:
                if r in owned:
                    if "tiers" in v:
                        try:
                            v["cost"] = v["tiers"][tcount]
                        except IndexError:
                            v["cost"] = 1
                    avaliable.append({"name":skin, **v})
                    break
        elif "needed" in v:
            a = True
            for r in v["needed"]:
                if not r in owned:
                    a = False
            if a:
                avaliable.append({"name":skin, **v})
        else:
            avaliable.append({"name":skin, **v})

    return render_template("skins.html", score=floor(session["score"]), skins=avaliable, owned=owned)

@app.route("/skins/<file>", methods=["GET"])
def skins(file):
    return send_file("static/skins/" + file)

@socketio.on("connect")
def connect():
    if not "id" in session:
        session["id"] = str(request.remote_addr)
    if not "name" in session:
        session["name"] = "User"
    if not "skin" in session:
        session["skin"] = choice(free_skins)
    print("initialized")
    if not treasures["main"]["shown"]:
        spawn_treasure()
    print("items spawned")
    x = 34
    y = 16
    session["map"] = "main"
    session["score"] = get_score(session["id"], 0)
    maps[session["map"]]["players"][session["id"]] = {
        "name": session["name"],
        "locationX": x,
        "locationY": y,
        "radius": randrange(30) / 100 + 0.4,
        "direction": "d",
        "chat": "",
        "score": floor(session["score"]),
        "view_radius": maps[session["map"]]["elevation"][y][x],
        "skin": {
            "name": session["skin"],
            "width": all_skins[session["skin"]]["radius"]
        }
    }
    try:
        join_room(session["map"])
        join_room(session["id"])
        emit("id", [session["id"]], broadcast=True, namespace="/", room=session["id"])
        leave_room(session["id"])
    except:
        pass
    emit("sound", "cloud", broadcast=False)
    refresh()

@socketio.on("disconnect")
def leave():
    save_session(session["score"])
    print("\ndisconnect\n")
    try:
        leave_room(session["map"])
        try:
            maps[session["map"]]["players"].pop(session["id"])
        except:
            print("error with disconnection")
        refresh()
    except:
        print("error with disconnection")
        pass

@socketio.on("refresh")
def refresh():
    emit("update", [send(maps[session["map"]])], broadcast=True, namespace="/", room=session["map"])

@socketio.on("skin")
def skin_check(skin):
    session["skin"] = skin
    maps[session["map"]]["players"][session["id"]]["skin"] = {
        "name": session["skin"],
        "width": all_skins[session["skin"]]["radius"]
    }

@socketio.on("chat")
def chatted(message):
    session["score"] += 0.08
    maps[session["map"]]["players"][session["id"]]["score"] = floor(session["score"])
    chat(maps[session["map"]]["players"][session["id"]], profanity.censor(message))
    if session["map"] == treasures["main"]["world"] and abs(maps[session["map"]]["players"][session["id"]]["locationX"] - treasures["main"]["x"]) < 2 and abs(maps[session["map"]]["players"][session["id"]]["locationY"] - treasures["main"]["y"]) < 2 and len(maps[session["map"]]["players"][session["id"]]["chat"]) > 0:
        warp(maps[session["map"]]["players"][session["id"]], maps[session["map"]], "treasure")
    if session["map"] == treasures["redshroom"][0]["world"] and abs(maps[session["map"]]["players"][session["id"]]["locationX"] - treasures["redshroom"][0]["x"]) < 2 and abs(maps[session["map"]]["players"][session["id"]]["locationY"] - treasures["redshroom"][0]["y"]) < 2 and len(maps[session["map"]]["players"][session["id"]]["chat"]) > 0:
        warp(maps[session["map"]]["players"][session["id"]], maps[session["map"]], "mushroom")
    if maps[session["map"]]["players"][session["id"]]["chat"] == "CURSED":
        warp(maps[session["map"]]["players"][session["id"]], maps[session["map"]], "cursed")
    refresh()

@socketio.on("movement")
def movement(dir):
    move(maps[session["map"]]["players"][session["id"]], dir, maps[session["map"]])
    refresh()

socketio.run(app, host="0.0.0.0", port=5000)
