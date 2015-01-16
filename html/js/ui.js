/* 
 * vim: set tabstop=4:shiftwidth=4
 */

var plotdata_t_ext = [20, 25, 30, 34, 38, 41, 44, 47, 50],
	plotdata_t_bed = [20, 20, 20, 20, 21, 21, 21, 22, 22],
	plotdata_mov = [[0, 0], [40, 40], [50, 40]];

var actual_z = 0;

function draw_axes(id, ymin, ymax)
{
	var canvas = document.getElementById(id);
	if (null==canvas || !canvas.getContext) return;

	ctx=canvas.getContext("2d");
	ctx.beginPath();
	ctx.strokeStyle = "rgb(128, 128, 128)";
	ctx.moveTo(20, 0);
	ctx.lineTo(20, canvas.height);
	ctx.moveTo(0, canvas.height - 20);
	ctx.lineTo(canvas.width, canvas.height - 20);
	ctx.stroke();
}

function draw_movements(id, data)
{
	var canvas = document.getElementById(id);
	var i, h;
	var len = data.length;

	if (null==canvas || !canvas.getContext) return;

	/* Set canvas pixel size */
	canvas.width = canvas.clientWidth;
	canvas.height = canvas.clientHeight;
	log("Canvas (mov) :" + String(canvas.width) + " x " + String(canvas.height));
	h = canvas.height - 5;

	ctx=canvas.getContext("2d");
	ctx.clearRect(0, 0, canvas.width, canvas.height);
	ctx.beginPath();
	ctx.strokeStyle = "rgb(128, 128, 128)";
	ctx.rect(0, h - 185, 195, h);
	ctx.stroke();
	ctx.beginPath();
	ctx.strokeStyle = "rgb(0, 128, 255)";
	p = data[0];
	ctx.moveTo(p[0], h - p[1]);
	for (i = 1; i < len; i ++) {
		p = data[i];
		ctx.lineTo(p[0], h - p[1]);
	}
	ctx.stroke();
}


function draw_plot(id, data)
{
	var canvas = document.getElementById(id);
	var i;
	var len = data.length;
	var ymin = 20, ymax = 100,
		yrange, ypltrange, xpltrange;

	if (null==canvas || !canvas.getContext) return;

	/* Set canvas pixel size */
	canvas.width = canvas.clientWidth;
	canvas.height = canvas.clientHeight;
	log("Canvas :" + String(canvas.width) + " x " + String(canvas.height));

	for (i = 0; i < len; i ++) {
		if (data[i] > ymax)
			ymax = data[i];
		if (data[i] < ymin)
			ymin = data[i];
	}
	ymin = Math.floor(ymin / 10) * 10;
	ymax = Math.ceil(ymax / 10) * 10;
	yrange = ymax - ymin;
	ypltrange = canvas.height - 20;
	xpltrange = canvas.width - 20;
	draw_axes(id, ymin, ymax);
	ctx=canvas.getContext("2d");
	ctx.beginPath();
	ctx.strokeStyle = "rgb(255, 0, 0)";
	for (i = 0; i < (len - 1); i ++) {
		var x1 = 20 + (i * xpltrange) / (len - 1);
		var x2 = 20 + ((i + 1) * xpltrange) / (len - 1);
		if (i == 0) {
			ctx.moveTo(x1, ypltrange - (data[i] * ypltrange) / yrange);
		}
		ctx.lineTo(x2, ypltrange - (data[i + 1] * ypltrange) / yrange);
	}
	ctx.stroke();
}

function add_plot_data(data, x, reset)
{
	if (reset) {
		data.length = 0;
		log("plot reset");
	}
	data.push(x);
	if (data.length >= 3600) {
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
