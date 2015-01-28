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

function WSParseTemp(obj)
{
	add_plot_data(plotdata_t_ext, obj.extruder);
	add_plot_data(plotdata_t_bed, obj.bed);
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

var printer_status = "idle";
var extruder_status = "off";
var bed_status = "off";

function WSParseStatus(obj)
{
	printer_status = obj.motors;
	extruder_status = obj.extruder;
	bed_status = obj.bed;
	var sline = document.getElementById("div_statline");

	log("Status: " + printer_status + " " + extruder_status + " " + bed_status);
	if (printer_status == "idle") {
		block_move_buttons(false);
	} else {
		block_move_buttons(true);
	}
	sline.innerHTML = "<table id='table_statline'><tr><td>Status: " +
		printer_status + "</td><td>Extruder: " + extruder_status +
		"</td><td>Bed: " + bed_status + "</td></tr></table>";
}

function WSHandler(txt)
{
	var obj = JSON.parse(txt.data);
	var id = obj.id;

	// log(txt.data);

	switch(id) {
	case "temperature":
		WSParseTemp(obj);
		break;
	case "move":
		WSParseMove(obj);
		break;
	case "status":
		WSParseStatus(obj);
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


