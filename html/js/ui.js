/* 
 * vim: set tabstop=4:shiftwidth=4
 */

var plotdata_t_ext = [220, 225],
	plotdata_t_bed = [95, 96],
	plotdata_mov = [[0, 0], [40, 40]];

var actual_z = 0, actual_e = 0, actual_layer = 0;

function draw_axes(id, ymin, ymax)
{
	var canvas = document.getElementById(id);
	var div;
	var divs = [1, 2, 5, 10, 20, 50];
	var rng = ymax - ymin;
	var i, dist;
	var yrng = canvas.height - 10;
	var y;

	if (null==canvas || !canvas.getContext) return;

	for (i = 0; i < divs.length; i ++) {
		div = divs[i];
		if ((rng / div) <= 10)
			break;
	}
	dist = rng / div;
	log("div = "+String(div)+" dist = " + String(dist));

	ctx=canvas.getContext("2d");
	ctx.beginPath();
	ctx.strokeStyle = "rgb(128, 128, 128)";
	ctx.moveTo(10, 10);
	ctx.lineTo(10, canvas.height);
	ctx.moveTo(10, canvas.height - 10);
	ctx.lineTo(canvas.width, canvas.height - 10);
	i = ymin;
	while (i < ymax) {
		y = yrng - ((i - ymin) * yrng) / rng;
		ctx.fillText(String(i), 0, y)
		ctx.moveTo(10, y);
		ctx.lineTo(canvas.width, y);
		i += div;
	}
	ctx.stroke();
}

var mov_canvas_w = 0, mov_canvas_h = 0;

function clear_movements(id)
{
	var canvas = document.getElementById(id);

	if (null==canvas || !canvas.getContext) return;

	ctx=canvas.getContext("2d");
	ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function fade_movements(id)
{
	var canvas = document.getElementById(id);

	if (null==canvas || !canvas.getContext) return;

	ctx=canvas.getContext("2d");
	ctx.fillStyle="white";
	ctx.globalAlpha=0.5;
	ctx.fillRect(0, 0, canvas.width, canvas.height);
	ctx.globalAlpha=1.0;
}

function draw_movements(id, data)
{
	var canvas = document.getElementById(id);
	var i, h;
	var len = data.length;
	var mag = 2.0;
	var t0 = 1;
	var x, y;
	var greycomp = "0";
	var redraw = false;
	var startidx = len - 2;

	if (null==canvas || !canvas.getContext) return;

	/* Set canvas pixel size */
	if (canvas.width != canvas.clientWidth) {
		canvas.width = canvas.clientWidth;
		redraw = true;
	}
	if (canvas.height != canvas.clientHeight) {
		canvas.height = canvas.clientHeight;
		redraw = true;
	}
	h = canvas.height - 5;

	ctx=canvas.getContext("2d");
	if (redraw) {
		ctx.clearRect(0, 0, canvas.width, canvas.height);
		startidx = 0;
	}
	ctx.beginPath();
	ctx.strokeStyle = "rgb(128, 128, 128)";
	ctx.rect(5, 5, 185 * mag, 195 * mag);
	ctx.stroke();
	ctx.beginPath();
	ctx.strokeStyle = "rgb(" + greycomp +", 128, 255)";
	p = data[startidx];
	x = p[0] * mag;
	y = h - p[1] * mag;
	ctx.moveTo(x, y);
	for (i = startidx + 1; i < len; i ++) {
		p = data[i];
		if (p[3] != t0) {
			t0 = p[3];
			ctx.stroke();
			ctx.beginPath();
			ctx.moveTo(x, y);
			if (t0 == 0)
				ctx.strokeStyle = "rgb(255, 128, "+greycomp+")";
			else
				ctx.strokeStyle = "rgb("+greycomp+", 128, 255)";
		}
		x = p[0] * mag;
		y = h - p[1] * mag;
		ctx.lineTo(x, y);
	}
	ctx.stroke();
}

function draw_plot(id, data)
{
	var canvas = document.getElementById(id);
	var i;
	var len = data.length;
	var ymin = 100, ymax = 150,
		yrange, ypltrange, xpltrange;

	if (null==canvas || !canvas.getContext) return;

	/* Set canvas pixel size */
	canvas.width = canvas.clientWidth;
	canvas.height = canvas.clientHeight;

	for (i = 0; i < len; i ++) {
		if (data[i] > ymax)
			ymax = data[i];
		if (data[i] < ymin)
			ymin = data[i];
	}
	ymin = Math.floor(ymin / 10) * 10;
	ymax = Math.ceil(ymax / 10) * 10;
	yrange = ymax - ymin;
	ypltrange = canvas.height - 10;
	xpltrange = canvas.width - 10;
	draw_axes(id, ymin, ymax);
	ctx=canvas.getContext("2d");
	ctx.beginPath();
	ctx.strokeStyle = "rgb(255, 0, 0)";
	for (i = 0; i < (len - 1); i ++) {
		var x1 = 10 + (i * xpltrange) / (len - 1);
		var x2 = 10 + ((i + 1) * xpltrange) / (len - 1);
		if (i == 0) {
			ctx.moveTo(x1, ypltrange - ((data[i] - ymin) * ypltrange) / yrange);
		}
		ctx.lineTo(x2, ypltrange - ((data[i + 1] - ymin) * ypltrange) / yrange);
	}
	ctx.stroke();
}

function add_plot_data(data, x, reset)
{
	if (reset) {
		data.length = 0;
		log("plot reset");
		fade_movements("canvas_mov");
	}
	data.push(x);
	if (data.length >= 1800) {
		data.shift();
	}
}

function UIInit()
{
	log("UI Init");
	draw_plot("canvas_t_ext", plotdata_t_ext);
	draw_plot("canvas_t_bed", plotdata_t_bed);
	draw_movements("canvas_mov", plotdata_mov);
}

function btnStart()
{
	var cmd = new WSCommand("runfile");
	cmd.filename = document.getElementById("filename_entry").value;
	WSSendObject(cmd);
}

function btnGcode()
{
	var cmd = new WSCommand("gcode");
	cmd.code = document.getElementById("gcode_entry").value;
	WSSendObject(cmd);
}

function btnHome()
{
	var cmd = new WSCommand("gcode");
	cmd.code = "G28"
	if (document.getElementById("homex_check").checked)
		cmd.code += " X0";
	if (document.getElementById("homey_check").checked)
		cmd.code += " Y0";
	if (document.getElementById("homez_check").checked)
		cmd.code += " Z0";
	if (cmd.code.length > 3)
		WSSendObject(cmd);
}

function btnMove(axis)
{
	var cmd = new WSCommand("gcode");
	cmd.code = "G91"; // Relative mode
	WSSendObject(cmd);
	cmd.code = "G1 " + axis + document.getElementById("distance_entry").value;
	cmd.code += " F" + document.getElementById("feedrate_entry").value;
	WSSendObject(cmd);
	cmd.code = "G90"; // Absolute mode
	WSSendObject(cmd);
}

function block_move_buttons(block)
{
	var btns = document.getElementsByClassName("gcodebtn");
	var n = btns.length;
	var i;

	for (i = 0; i < n; i ++) {
		btns[i].disabled = block;
	}
}
