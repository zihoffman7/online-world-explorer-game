var socket, id;
var emittable = true;
const PAUSE_TIME = 82;
var mmap = false;

function rotate(image, angle, width) {
  width = Math.floor(width);
  ang = (angle == "d") ? -Math.PI / 2 : (angle == "u") ?  Math.PI / 2 : (angle == "l") ? 0 : Math.PI;
  var offscreenCanvas = document.createElement("canvas");
  var offscreenCtx = offscreenCanvas.getContext("2d");
  offscreenCanvas.width = width;
  offscreenCanvas.height = width;
  offscreenCtx.translate((angle == "u" || angle == "l") ? width : 0, (angle == "u" || angle == "r") ? width : 0);
  offscreenCtx.rotate(ang + Math.PI / 2);
  offscreenCtx.drawImage(image, 0, 0, width, width);
  return offscreenCanvas;
}

(function() {

  socket = io();

  document.addEventListener("beforeunload", function() {
    socket.disconnect();
  });

  socket.on("sound", function(name) {
    sounds[name].play();
  });

  socket.on("stopsound", function() {
    for (var item in sounds) {
      sounds[item].stop();
    }
  });

  socket.on("update", function(data) {
    try {
      data[0].player = JSON.parse(JSON.stringify(data[0].players[0][id]));
      data[0].viewRadius = JSON.parse(JSON.stringify(data[0].players[0][id]["view_radius"]));
      delete data[0].players[0][id];
      update(data[0]);
    }
    catch(err) {
      console.log(err);
    }
  });

  socket.on("id",  function(data) {
    id = data[0];
  });

  document.addEventListener("keydown", function(e) {
    if (!mmap && e.key == "m") {
      mmap = true;
      document.getElementById("minimap").style.visibility = "visible";
    }
    if (emittable && !mmap) {
      if (e.key == "Right"  || e.key == "ArrowRight") {
        socket.emit("movement", "r");
      }
      if (e.key == "Left"  || e.key == "ArrowLeft") {
        socket.emit("movement", "l");
      }
      if (e.key == "Up"  || e.key == "ArrowUp") {
        socket.emit("movement", "u");
      }
      if (e.key == "Down"  || e.key == "ArrowDown") {
        socket.emit("movement", "d");
      }
      emittable = false;
      setTimeout(function() {
        emittable = true;
      }, PAUSE_TIME);
    }
  });

  document.addEventListener("keyup", function(e) {
    if (e.key == "m") {
      reMap();
    }
  });
})();

function reMap() {
  if (mmap) {
    mmap = false;
    document.getElementById("minimap").style.visibility = "hidden";
  }
}

function fillMinimap(data, viewR) {
  if (!data.hidden) {
    document.getElementById("minimap").style.visibility = "hidden";
    return;
  }
  mcanvas.width = 140;
  mcanvas.height = 140;
  var mWidth = Math.floor(mcanvas.width / (viewR * 2 + 1));
  mcanvas.width = mWidth * (viewR * 2 + 1);
  mcanvas.height = mWidth * (viewR* 2 + 1);
  var mX = data.player.locationX - Math.floor(viewR), mY = data.player.locationY - Math.floor(viewR);
  for (var y = mY; y < data.player.locationY + Math.floor(viewR) + 1; y++) {
    for (var x = mX; x < data.player.locationX + Math.floor(viewR) + 1; x++) {
      mctx.fillStyle = "white";
      if (x > -1 && y > -1 && y < data.boardColors.length && x < data.boardColors[0].length) {
        if (data.boardColors[y][x].length == 3) {
          mctx.fillStyle = "pink";
        }
        else if (data.boardColors[y][x].length == 4) {
          mctx.fillStyle = data.boardColors[y][x][3];
        }
        else {
          mctx.fillStyle = data.boardColors[y][x];
        }
      }
      else {
        mctx.fillStyle = data.background;
      }
      mctx.fillRect((x - mX)*mWidth, (y - mY)*mWidth, (x - mX)*mWidth + mWidth, (y - mY)*mWidth + mWidth);
    }
  }

  if (data.players.length) {
    mctx.fillStyle = "red";
    for (var player of Object.keys(data.players[0])) {
      player = data.players[0][player];
      if (!player) {
        continue;
      }
      mctx.fillRect((player.locationX - mX)*mWidth, (player.locationY - mY)*mWidth, mWidth, mWidth);
    }
  }
  mctx.fillStyle = "orange";
  mctx.fillRect((data.player.locationX - mX)*mWidth, (data.player.locationY - mY)*mWidth, mWidth, mWidth);
}

function update(data) {
  canvas.width = 400;
  canvas.height = 400;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  var squareWidth = Math.floor(canvas.width / (data.viewRadius * 2 + 1));
  canvas.width = squareWidth * (data.viewRadius * 2 + 1);
  canvas.height = squareWidth * (data.viewRadius * 2 + 1);
  var t = [];
  var placedX = data.player.locationX - Math.floor(data.viewRadius), placedY = data.player.locationY - Math.floor(data.viewRadius);
  for (var y = placedY; y < data.player.locationY + Math.floor(data.viewRadius) + 1; y++) {
    for (var x = placedX; x < data.player.locationX + Math.floor(data.viewRadius) + 1; x++) {
      ctx.fillStyle = "white";
      if (x > -1 && y > -1 && y < data.boardColors.length && x < data.boardColors[0].length) {
        if (data.boardColors[y][x].length == 3) {
          var grd = ctx.createRadialGradient(
            (x - placedX)*squareWidth + squareWidth / 2, (y - placedY)*squareWidth + squareWidth / 2, squareWidth / 2,
            (x - placedX)*squareWidth + squareWidth / 2, (y - placedY)*squareWidth + squareWidth / 2, squareWidth * 0.2
          );
          grd.addColorStop(0, data.boardColors[y][x][0]);
          grd.addColorStop(0.5, data.boardColors[y][x][1]);
          grd.addColorStop(0.9, data.boardColors[y][x][2]);
          grd.addColorStop(1, data.boardColors[y][x][1]);
          ctx.fillStyle = grd;
        }
        else if (data.boardColors[y][x].length == 4) {
          ctx.fillStyle = data.boardColors[y][x][3];
          ctx.fillRect((x - placedX)*squareWidth, (y - placedY)*squareWidth, (x - placedX)*squareWidth + squareWidth, (y - placedY)*squareWidth + squareWidth);
          t.push({
            img: rotate(skins[data.boardColors[y][x][0]], data.boardColors[y][x][1], data.boardColors[y][x][2] * squareWidth),
            x: x, y: y
          });
          continue;
        }
        else {
          ctx.fillStyle = data.boardColors[y][x];
        }
      }
      else {
        ctx.fillStyle = data.background;
      }
      ctx.fillRect((x - placedX)*squareWidth, (y - placedY)*squareWidth, (x - placedX)*squareWidth + squareWidth, (y - placedY)*squareWidth + squareWidth);
    }
  }
  fillMinimap(data, 15);

  for (var tr of t) {
    ctx.drawImage(tr.img, (tr.x - placedX)*squareWidth + Math.floor(squareWidth / 2) - tr.img.width / 2, (tr.y - placedY)*squareWidth + Math.floor(squareWidth / 2) - tr.img.width / 2);
    ctx.restore();
  }
  var player, img, rotated;
  if (data.treasure.length) {
    rotated = rotate(skins["treasure"], data.treasure[3], data.treasure[2] * squareWidth)
    ctx.drawImage(rotated, (data.treasure[0] - placedX)*squareWidth + Math.floor(squareWidth / 2) - rotated.width / 2, (data.treasure[1] - placedY)*squareWidth + Math.floor(squareWidth / 2) - rotated.width / 2);
    ctx.restore();
  }
  for (var item of data.items) {
    rotated = rotate(skins[item.img.split("/")[1].split(".")[0]], item.dir, item.size * squareWidth)
    ctx.drawImage(rotated, (item.x - placedX)*squareWidth + Math.floor(squareWidth / 2) - rotated.width / 2, (item.y - placedY)*squareWidth + Math.floor(squareWidth / 2) - rotated.width / 2);
    ctx.restore();
  }
  if (data.players.length) {
    for (var player of Object.keys(data.players[0])) {
      player = data.players[0][player];
      if (!player) {
        continue;
      }
      img = skins[player.skin.name];
      rotated = rotate(img, player.direction, player.skin.width * squareWidth)
      ctx.drawImage(rotated, (player.locationX - placedX)*squareWidth + Math.floor(squareWidth / 2) - rotated.width / 2, (player.locationY - placedY)*squareWidth + Math.floor(squareWidth / 2) - rotated.width / 2);
      ctx.restore();

      ctx.font = "10px Arial";
      ctx.textAlign="center";
      ctx.textBaseline = "middle";
      ctx.fillStyle = (data.mapName == "snow" || data.mapName == "cloud") ? "darkslategray" : "white";
      ctx.fillText(`${player.name} (${player.score || "0"})`, (player.locationX - placedX)*squareWidth + Math.floor(squareWidth / 2), (player.locationY - placedY)*squareWidth + Math.floor(squareWidth / 2) - rotated.width / 2 + (player.skin.width) * squareWidth + 4);
    }
  }
  img = skins[data.player.skin.name];
  rotated = rotate(img, data.player.direction, data.player.skin.width * squareWidth)
  ctx.drawImage(rotated, (data.player.locationX - placedX)*squareWidth + Math.floor(squareWidth / 2) - rotated.width / 2,  (data.player.locationY - placedY)*squareWidth + Math.floor(squareWidth / 2) - rotated.width / 2);
  ctx.restore();
  ctx.font = "10px Arial";
  ctx.textAlign="center";
  ctx.textBaseline = "middle";
  ctx.fillStyle = (data.mapName == "snow" || data.mapName == "cloud") ? "darkslategray" : "white";
  ctx.fillText(`${data.player.name} (${data.player.score || "0"})`, Math.floor(canvas.width / 2), (data.player.locationY - placedY)*squareWidth + Math.floor(squareWidth / 2) - rotated.width / 2 + (data.player.skin.width) * squareWidth + 4);

  if (data.player.chat) {
    ctx.fillStyle = "rgb(125, 125, 125, 0.7)";
    ctx.fillRect(canvas.width/2 - 4 * data.player.chat.length, Math.floor(canvas.height / 2) - data.player.skin.width/2 * squareWidth - 30, 8 * data.player.chat.length, 24);
    ctx.font="16px Arial";
    ctx.textAlign="center";
    ctx.textBaseline = "middle";
    ctx.fillStyle = "white";
    ctx.fillText(data.player.chat, Math.floor(canvas.width / 2), Math.floor(canvas.height / 2) - data.player.skin.width/2 * squareWidth - 18);
  }

  if (data.players.length) {
    for (var player of Object.keys(data.players[0])) {
      player = data.players[0][player];
      if (!player) {
        continue;
      }
      if (!player.chat) {
        continue;
      }
      ctx.fillStyle = "rgb(100, 100, 100, 0.7)";
      ctx.fillRect((player.locationX - placedX)*squareWidth + Math.floor(squareWidth / 2) - 4 * player.chat.length, (player.locationY - placedY)*squareWidth + Math.floor(squareWidth / 2) - player.skin.width/2 * squareWidth - 35, 8 * player.chat.length, 30);
      ctx.font="16px Arial";
      ctx.textAlign="center";
      ctx.textBaseline = "middle";
      ctx.fillStyle = "white";
      ctx.fillText(player.chat, (player.locationX - placedX)*squareWidth + Math.floor(squareWidth / 2), (player.locationY - placedY)*squareWidth + Math.floor(squareWidth / 2) - player.skin.width/2 * squareWidth - 20);
    }

    ctx.textAlign = "left";
    ctx.font="12px Arial";
    ctx.fillStyle = (data.mapName == "snow" || data.mapName == "cloud") ? "darkslategray" : "white";
    ctx.fillText("Online: " + data.count, 4, 12);
    ctx.textAlign = "right";
    ctx.fillText("treasure: " + data.treasureData, canvas.width - 4, 12);
    ctx.fillText(`location: ${data.mapName} (${data.player.locationX}, ${data.boardColors.length-data.player.locationY})`, canvas.width - 4, 26);
  }

  var chattable = true;
  document.getElementById("chat").addEventListener("submit", function(e) {
    e.preventDefault();
    if (chattable && document.getElementById("message").value.length) {
      socket.emit("chat", document.getElementById("message").value);
      document.getElementById("message").value = "";
      document.getElementById("message").readOnly = true;
      document.getElementById("message").placeholder = "Can't chat yet";
      chattable = false;
      setTimeout(function() {
        chattable = true;
        document.getElementById("message").placeholder = "Message here";
        document.getElementById("message").readOnly = false;
      }, 2500);
    }
  });
}

function sound(src, volume, loop) {
  this.sound = document.createElement("audio");
  this.sound.src = src;
  this.sound.loop = loop;
  this.sound.volume = volume;
  this.sound.setAttribute("preload", "auto");
  this.sound.setAttribute("controls", "none");
  this.sound.style.display = "none";
  document.body.appendChild(this.sound);
  this.play = function(){
    this.sound.play();
  }
  this.stop = function(){
    this.sound.pause();
  }
}
