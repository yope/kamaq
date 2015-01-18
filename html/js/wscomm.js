/* 
 * vim: set tabstop=4:shiftwidth=4
 */

var ws_conn;
var ws_initialized = false;

var startTime = (new Date()).getTime();
function log(s)
{
	var ti = (new Date()).getTime() - startTime;
	console.log((ti/1000.0).toFixed(3) + "   : " + s);
}

function WSParseStatus(obj)
{
	add_plot_data(plotdata_t_ext, obj.temp_ext);
	add_plot_data(plotdata_t_bed, obj.temp_bed);
	draw_plot("canvas_t_ext", plotdata_t_ext);
	draw_plot("canvas_t_bed", plotdata_t_bed);
}

function WSParseMove(obj)
{
	var p = [obj.x, obj.y];
	var reset = false;
	var type = 1;

	if (obj.z != actual_z) {
		actual_z = obj.z;
		reset = true;
	}
	if (obj.e <= actual_e) {
		log("Type 0");
		type = 0;
	}
	actual_e = obj.e;
	var p = [obj.x, obj.y, obj.z, type];
	add_plot_data(plotdata_mov, p, reset);
	draw_movements("canvas_mov", plotdata_mov);
}

function WSHandler(txt)
{
	var obj = JSON.parse(txt.data);
	var id = obj.id;

	// log(txt.data);

	switch(id) {
	case "status":
		WSParseStatus(obj);
		break;
	case "move":
		WSParseMove(obj);
		break;
	default:
		break;
	}
}

function WSInit()
{
	ws_conn = new WebSocket("ws://"+window.location.hostname+":9999/");
	ws_conn.onopen = function () {
		ws_initialized = true;
		WSSendObject(new WSCommand("hello"));
	}
	ws_conn.onmessage = WSHandler;
}

function WSCommand(cmd)
{
	this.command = cmd;
}

function WSSendObject(obj)
{
	var txt = JSON.stringify(obj);
	ws_conn.send(txt);
}


